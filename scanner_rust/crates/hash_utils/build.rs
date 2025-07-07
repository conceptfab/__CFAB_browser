use vergen::{vergen, Config};

fn main() {
    // Generuj informacje o kompilacji
    let mut config = Config::default();
    *config.build_mut().timestamp_mut() = true;
    *config.cargo_mut().target_triple_mut() = true;
    
    vergen(config).expect("Failed to generate build information");
} 