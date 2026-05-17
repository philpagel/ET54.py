// ET44xx / ET45xx firmware updater

use anyhow::{bail, Context, Result};
use clap::Parser;
use serialport::SerialPort;
use encoding_rs::GBK;
use std::{
    fs,
    io::{Read, Write},
    thread,
    time::{Duration, Instant},
};


#[derive(Parser, Debug)]
#[command(
    author,
    version,
    about = "ET54xx electronic load firmware updater"
)]
struct Args {
    /// Serial device / COM port
    #[arg(short, long, default_value = default_serial_port())]
    serialdev: String,
    
    /// baud rate
    #[arg(short, long, default_value = "14400")]
    baudrate: u32,

    /// Suppress console output
    #[arg(short, long)]
    quiet: bool,

    /// Firmware hex file
    hexfile: String,
}

fn default_serial_port() -> &'static str {
    #[cfg(windows)]
    {
        "COM1"
    }

    #[cfg(not(windows))]
    {
        "/dev/ttyUSB0"
    }
}

struct Logger {
    quiet: bool,
}

impl Logger {
    fn new(quiet: bool) -> Self {
        Self { quiet }
    }

    fn log(&self, msg: impl AsRef<str>) {
        if !self.quiet {
            println!("{}", msg.as_ref());
        }
    }

    fn print(&self, msg: impl AsRef<str>) {
        if !self.quiet {
            print!("{}", msg.as_ref());
            let _ = std::io::stdout().flush();
        }
    }
}

fn main() -> Result<()> {
    let args = Args::parse();
    let logger = Logger::new(args.quiet);

    let mut port = serialport::new(&args.serialdev, args.baudrate)
        .timeout(Duration::from_millis(100))
        .open()
        .with_context(|| format!("Cannot open serial device {}", args.serialdev))?;

    port.clear(serialport::ClearBuffer::All)?;

    trigger_bootloader(&mut *port, &logger)?;
    handle_menu(&mut *port, 1, &logger)?;
    upload_firmware(&mut *port, &args.hexfile, &logger)?;
    handle_response(&mut *port, &logger)?;

    logger.log("Wait for load to display 'Please Reset!' before cycling power.");

    Ok(())
}

fn trigger_bootloader(port: &mut dyn SerialPort, logger: &Logger) -> Result<()> {
    logger.log("Sending magic number. Please turn on the device now.");

    const MAGIC: &[u8] = &[0x1b, 0x42, 0x54, 0x39, 0x36, 0x05, 0x7a];
    let mut pos = 0usize;
    let mut dir: isize = 1;

    loop {
        let mut light = [' '; 10];
        light[pos] = '.';

        logger.print(format!("\r{}", light.iter().collect::<String>()));

        port.write_all(MAGIC)?;
        port.flush()?;

        thread::sleep(Duration::from_millis(70));

        let waiting = port.bytes_to_read()?;
        if waiting > 0 {
            break;
        }

        if pos == 9 {
            dir = -1;
        } else if pos == 0 {
            dir = 1;
        }

        pos = ((pos as isize) + dir) as usize;
    }

    logger.log("");

    Ok(())
}

fn handle_menu(
    port: &mut dyn SerialPort,
    item: u8,
    logger: &Logger,
) -> Result<()> {
    let mut menu_complete = false;
    let mut selected = false;

    loop {
        let line = read_line(port)?;

        if !line.is_empty() {
            logger.log(format!("> {}", line));
        }

        if line.contains("帮助") {
            menu_complete = true;
        }

        if menu_complete && line.contains("----------------------") {
            let selection = [b'0' + item];
            port.write_all(&selection)?;
            port.flush()?;

            logger.log(format!("Selecting: [{}].", item));
            selected = true;
        }

        if item == 1 && line.contains("准备接收文件") {
            return Ok(());
        }

        if item == 2 && selected {
            thread::sleep(Duration::from_millis(500));
            return Ok(());
        }
    }
}

fn upload_firmware(
    port: &mut dyn SerialPort,
    hexfile: &str,
    logger: &Logger,
) -> Result<()> {
    let contents = fs::read_to_string(hexfile)
        .with_context(|| format!("Failed to read {}", hexfile))?;

    let lines: Vec<_> = contents.lines().collect();
    let total = lines.len();

    logger.log(format!("Uploading '{}'", hexfile));

    for (index, line) in lines.iter().enumerate() {
        let mut payload = line.as_bytes().to_vec();
        payload.push(b'\n');

        port.write_all(&payload)?;
        port.flush()?;

        let percent = ((index + 1) as f32 / total as f32) * 100.0;

        logger.print(format!(
            "\rProgress: {}/{} rows {:.0}%",
            index + 1,
            total,
            percent
        ));
        if index + 1 < total {
            wait_for_ack(port)?;
        }
    }

    logger.log("");

    Ok(())
}

fn wait_for_ack(port: &mut dyn SerialPort) -> Result<()> {
    let timeout = Instant::now() + Duration::from_secs(5);

    loop {
        if Instant::now() > timeout {
            bail!("ACK timeout");
        }

        if port.bytes_to_read()? > 0 {
            let mut byte = [0u8; 1];
            port.read_exact(&mut byte)?;

            if byte[0] == b'.' {
                return Ok(());
            } else {
                bail!("Unexpected response during upload");
            }
        }

        thread::sleep(Duration::from_micros(100));
    }
}

fn handle_response(
    port: &mut dyn SerialPort,
    logger: &Logger,
) -> Result<()> {
    let mut deadline = Instant::now() + Duration::from_secs(2);

    loop {
        if Instant::now() > deadline {
            bail!("Timeout: no response from the device.");
        }

        let line = read_line(port)?;

        if !line.is_empty() {
            logger.log(format!("> {}", line));
            deadline = Instant::now() + Duration::from_secs(2);
        }

        if line.contains("空间溢出") {
            bail!("Buffer Overflow");
        }

        if line.contains("写入错误") {
            bail!("Write Error");
        }

        if line.contains("无效命令") {
            bail!("Invalid command");
        }

        if line.starts_with("***") && line.ends_with('!') {
            bail!("Unknown Error: '{}'", line);
        }

        if line.contains("下载成功!") {
            logger.log("Upload finished.");
            return Ok(());
        }
    }
}

fn read_line(port: &mut dyn SerialPort) -> Result<String> {
    let mut buffer = Vec::new();
    let mut byte = [0u8; 1];

    loop {
        match port.read(&mut byte) {
            Ok(1) => {
                if byte[0] == b'\n' {
                    break;
                }

                if byte[0] != b'\r' {
                    buffer.push(byte[0]);
                }
            }

            Ok(_) => {}

            Err(ref e) if e.kind() == std::io::ErrorKind::TimedOut => {
                break;
            }

            Err(e) => return Err(e.into()),
        }
    }

    let (decoded_cow, _encoding, _errors) = GBK.decode(&buffer);
    let buffer: String = decoded_cow.into_owned();

    Ok(buffer)
}
