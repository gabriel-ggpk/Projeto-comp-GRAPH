/// Projeto-comp-GRAPH: A graphics computation library
/// This library provides basic structures and functions for graphics computation projects.
pub mod graphics;

pub use graphics::*;

/// Library version information
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Get the library version
pub fn version() -> &'static str {
    VERSION
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_version() {
        assert!(!version().is_empty());
        assert_eq!(version(), "0.1.0");
    }
}
