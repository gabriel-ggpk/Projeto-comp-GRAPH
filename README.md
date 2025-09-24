# Projeto-comp-GRAPH

A graphics computation project written in Rust, providing basic structures and functionality for graphics programming and computational graphics applications.

## Setup

### Prerequisites

- [Rust](https://rustup.rs/) (version 1.70 or later)
- Cargo (comes with Rust)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/gabriel-ggpk/Projeto-comp-GRAPH.git
   cd Projeto-comp-GRAPH
   ```

2. Build the project:
   ```bash
   cargo build
   ```

3. Run the application:
   ```bash
   cargo run
   ```

## Development

### Building

```bash
# Debug build
cargo build

# Release build
cargo build --release
```

### Testing

```bash
# Run all tests
cargo test

# Run tests with verbose output
cargo test -- --nocapture
```

### Linting

```bash
# Check code with clippy
cargo clippy

# Format code
cargo fmt
```

### Running

```bash
# Run the main application
cargo run

# Run with release optimizations
cargo run --release
```

## Project Structure

```
src/
├── lib.rs          # Library root and public API
├── main.rs         # Application entry point
└── graphics.rs     # Basic graphics primitives and operations
```

## Features

- **Basic Graphics Primitives**: 2D points, colors, and basic operations
- **Modular Design**: Clean separation between library and application code
- **Comprehensive Testing**: Unit tests for all major functionality
- **Development Tools**: Linting, formatting, and testing infrastructure

## Library Usage

The project can be used both as a standalone application and as a library:

```rust
use projeto_comp_graph::{Point2D, Color};

// Create points
let origin = Point2D::origin();
let point = Point2D::new(3.0, 4.0);
let distance = origin.distance_to(&point);

// Create colors
let red = Color::red();
let custom = Color::rgb(128, 64, 192);
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Run tests: `cargo test`
5. Run linting: `cargo clippy`
6. Format code: `cargo fmt`
7. Commit your changes: `git commit -am 'Add some feature'`
8. Push to the branch: `git push origin feature-name`
9. Submit a pull request

## License

This project is open source. Please check the repository for license details.