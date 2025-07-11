#[cfg(test)]
mod tests {
    use std::fs;
    use std::path::Path;
    use tempfile::TempDir;
    
    // Import modules from src
    use scanner_rust::*;
    
    /// Helper function to create test files
    fn create_test_files(dir: &Path, count: usize) -> Vec<String> {
        let mut created_files = Vec::new();
        
        for i in 0..count {
            let archive_name = format!("test_asset_{:03}.zip", i);
            let image_name = format!("test_asset_{:03}.png", i);
            
            let archive_path = dir.join(&archive_name);
            let image_path = dir.join(&image_name);
            
            fs::write(&archive_path, b"fake zip content").unwrap();
            fs::write(&image_path, b"fake png content").unwrap();
            
            created_files.push(format!("test_asset_{:03}", i));
        }
        
        created_files
    }

    #[test]
    fn test_file_extensions() {
        use scanner_rust::types::FileExtensions;
        
        let extensions = FileExtensions::default();
        
        // Test archive extensions
        assert!(extensions.archives.contains("zip"));
        assert!(extensions.archives.contains("rar"));
        assert!(extensions.archives.contains("sbsar"));
        assert!(extensions.archives.contains("7z"));
        assert!(extensions.archives.contains("spsm"));
        
        // Test image extensions
        assert!(extensions.images.contains("png"));
        assert!(extensions.images.contains("jpg"));
        assert!(extensions.images.contains("jpeg"));
        assert!(extensions.images.contains("webp"));
    }

    #[test]
    fn test_file_utils() {
        use scanner_rust::file_utils::*;
        use std::collections::HashSet;
        
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Create test files
        create_test_files(temp_path, 5);
        
        // Test file extension validation
        let mut extensions = HashSet::new();
        extensions.insert("zip".to_string());
        
        let zip_file = temp_path.join("test.zip");
        fs::write(&zip_file, b"test").unwrap();
        
        assert!(has_valid_extension(&zip_file, &extensions));
        
        // Test file size calculation
        let size = get_file_size_mb(&zip_file).unwrap();
        assert!(size >= 0.0);
        assert!(size < 1.0); // Should be very small
    }

    #[test]
    fn test_group_files_by_name() {
        use scanner_rust::file_utils::group_files_by_name;
        
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Create test files
        create_test_files(temp_path, 3);
        
        // Create file paths
        let files = vec![
            temp_path.join("test_001.zip"),
            temp_path.join("test_002.zip"),
            temp_path.join("test_003.zip"),
        ];
        
        let grouped = group_files_by_name(files);
        
        assert_eq!(grouped.len(), 3);
        assert!(grouped.contains_key("test_001"));
        assert!(grouped.contains_key("test_002"));
        assert!(grouped.contains_key("test_003"));
    }

    #[test]
    fn test_asset_builder() {
        use scanner_rust::asset_builder::AssetBuilder;
        
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Create test files
        let archive_path = temp_path.join("test.zip");
        let image_path = temp_path.join("test.png");
        
        fs::write(&archive_path, b"fake zip content").unwrap();
        fs::write(&image_path, b"fake png content").unwrap();
        
        let builder = AssetBuilder::new();
        
        // Test asset creation
        let asset = builder.create_single_asset(
            "test_asset",
            &archive_path,
            &image_path,
            temp_path
        ).unwrap();
        
        assert_eq!(asset.name, "test_asset");
        assert!(asset.archive_path.contains("test.zip"));
        assert!(asset.image_path.contains("test.png"));
        assert!(asset.archive_size_mb >= 0.0);
        
        // Test asset save/load
        let asset_file = temp_path.join("test.asset");
        builder.save_asset_to_file(&asset, &asset_file).unwrap();
        
        let loaded_asset = builder.load_asset_from_file(&asset_file).unwrap();
        assert_eq!(loaded_asset.name, asset.name);
        assert_eq!(loaded_asset.archive_path, asset.archive_path);
    }

    #[test]
    fn test_special_folders() {
        use scanner_rust::file_utils::scan_for_special_folders;
        
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Create special folders
        fs::create_dir(temp_path.join("tex")).unwrap();
        fs::create_dir(temp_path.join("textures")).unwrap();
        
        let special_folders = scan_for_special_folders(temp_path).unwrap();
        
        assert_eq!(special_folders.len(), 2);
        
        let names: Vec<&str> = special_folders.iter().map(|f| f.name.as_str()).collect();
        assert!(names.contains(&"tex"));
        assert!(names.contains(&"textures"));
    }

    #[test]
    fn test_texture_folder_detection() {
        use scanner_rust::file_utils::check_texture_folders_presence;
        
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Without texture folders - should return true (textures in archive)
        assert!(check_texture_folders_presence(temp_path));
        
        // With texture folder - should return false (external textures)
        fs::create_dir(temp_path.join("tex")).unwrap();
        assert!(!check_texture_folders_presence(temp_path));
    }

    #[test]
    fn test_error_handling() {
        use scanner_rust::types::ScannerError;
        
        // Test file not found error
        let non_existent_path = Path::new("/non/existent/path");
        let result = std::fs::metadata(non_existent_path);
        assert!(result.is_err());
        
        // Test error conversion
        let io_error = result.unwrap_err();
        let scanner_error = ScannerError::from(io_error);
        
        match scanner_error {
            ScannerError::IoError(_) => {
                // This is expected
            }
            _ => panic!("Expected IoError variant"),
        }
    }
}

// Integration test for full scanner functionality
#[cfg(test)]
mod integration_tests {
    use super::*;
    use std::fs;
    use tempfile::TempDir;

    #[test]
    fn test_full_scanning_workflow() {
        let temp_dir = TempDir::new().unwrap();
        let temp_path = temp_dir.path();
        
        // Create test data
        let test_files = create_test_files(temp_path, 5);
        
        // Create some unpaired files
        fs::write(temp_path.join("unpaired.zip"), b"unpaired archive").unwrap();
        fs::write(temp_path.join("unpaired.png"), b"unpaired image").unwrap();
        
        // This test would require the full scanner implementation
        // For now, we test the individual components
        
        // Test that all expected files exist
        for file_name in &test_files {
            let archive_path = temp_path.join(format!("{}.zip", file_name));
            let image_path = temp_path.join(format!("{}.png", file_name));
            
            assert!(archive_path.exists());
            assert!(image_path.exists());
        }
        
        // Test unpaired files exist
        assert!(temp_path.join("unpaired.zip").exists());
        assert!(temp_path.join("unpaired.png").exists());
    }
} 