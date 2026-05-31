build: 
	cargo build --release
	cargo build --release --target x86_64-pc-windows-gnu

clean:
	cargo clean

deps:
	# setup dependencies for windows cross compiling
	apt install mingw-w64 
	rustup target add x86_64-pc-windows-gnu

.PHONEY: build clean deps
