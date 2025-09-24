use projeto_comp_graph::{version, Color, Point2D};

/// Entry point for the Projeto-comp-GRAPH application
fn main() {
    println!("Welcome to Projeto-comp-GRAPH v{}!", version());
    println!("Graphics computation project starting...");

    // Initialize basic application
    let app = GraphicsApp::new();
    app.run();
}

/// Basic graphics application structure
pub struct GraphicsApp {
    name: String,
}

impl GraphicsApp {
    /// Create a new graphics application instance
    pub fn new() -> Self {
        Self {
            name: "Projeto-comp-GRAPH".to_string(),
        }
    }

    /// Run the graphics application
    pub fn run(&self) {
        println!("Running {}...", self.name);

        // Demonstrate basic graphics functionality
        self.demo_graphics();

        println!("Setup complete! Ready for development.");
    }

    /// Get the application name
    pub fn name(&self) -> &str {
        &self.name
    }

    /// Demonstrate basic graphics functionality
    fn demo_graphics(&self) {
        println!("\n--- Graphics Demo ---");

        // Create some points
        let origin = Point2D::origin();
        let point = Point2D::new(3.0, 4.0);

        println!("Origin: {:?}", origin);
        println!("Point: {:?}", point);
        println!(
            "Distance from origin to point: {:.2}",
            origin.distance_to(&point)
        );

        // Create some colors
        let red = Color::red();
        let custom = Color::rgb(128, 64, 192);

        println!("Red color: {:?}", red);
        println!("Custom color: {:?}", custom);

        println!("--- End Demo ---\n");
    }
}

impl Default for GraphicsApp {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_graphics_app_creation() {
        let app = GraphicsApp::new();
        assert_eq!(app.name(), "Projeto-comp-GRAPH");
    }

    #[test]
    fn test_graphics_app_default() {
        let app = GraphicsApp::default();
        assert_eq!(app.name(), "Projeto-comp-GRAPH");
    }
}
