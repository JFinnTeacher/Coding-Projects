# Program: Word List Cleanup
# Purpose: Remove leading numbers and standardize word list format


# 1. Import required modules
import os  # File and directory operations
import re  # Regular expressions for pattern matching
import pathlib  # For path handling (more modern than os.path)
import argparse  # Command line argument parsing
from typing import List, Dict  # Type hints
from tqdm import tqdm  # Progress bars
import logging  # Logging functionality
from collections import Counter  # For tracking word frequencies

# 2. Define input/output functions
def get_input_files(directory: str, file_extensions: List[str] = ['.txt']) -> List[pathlib.Path]:
    """
    Get a list of files with specified extensions from the input directory.
    
    Args:
        directory (str): Path to the input directory
        file_extensions (List[str]): List of file extensions to include (default: ['.txt'])
    
    Returns:
        List[pathlib.Path]: List of Path objects for matching files
    
    Raises:
        FileNotFoundError: If directory doesn't exist
        PermissionError: If directory isn't accessible
    """
    try:
        # Convert directory to Path object
        dir_path = pathlib.Path(directory)
        
        # Check if directory exists
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        # Get all files with specified extensions
        files = []
        for ext in file_extensions:
            files.extend(dir_path.glob(f"*{ext}"))
        
        # Log number of files found
        logging.info(f"Found {len(files)} files with extensions {file_extensions}")
        
        return sorted(files)  # Return sorted list for consistent ordering
        
    except PermissionError:
        logging.error(f"Permission denied accessing directory: {directory}")
        raise
    except Exception as e:
        logging.error(f"Error accessing directory {directory}: {str(e)}")
        raise

def read_file_content(file_path: pathlib.Path) -> List[str]:
    """Read content from file and return as list of lines."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.readlines()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise

def write_cleaned_content(output_path: pathlib.Path, content: List[str]) -> None:
    """Write cleaned content to output file."""
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(content)
        logging.info(f"Successfully wrote cleaned content to {output_path}")
    except Exception as e:
        logging.error(f"Error writing to file {output_path}: {str(e)}")
        raise

# 3. Define cleanup functions
def clean_word_list(lines: List[str]) -> List[str]:
    """Apply all cleanup operations to the word list."""
    cleaned_words = []
    # Remove leading numbers, brackets, etc.
    number_pattern = r'^\s*(?:\d+[\.\)\]]|\[\d+\]|\(\d+\))\s*'
    
    for line in lines:
        # Strip whitespace and remove leading numbers
        cleaned = re.sub(number_pattern, '', line.strip())
        
        # Skip empty lines
        if not cleaned:
            continue
            
        # Convert to lowercase for standardization
        cleaned = cleaned.lower()
        
        cleaned_words.append(cleaned + '\n')
    
    # Remove duplicates while preserving order
    return list(dict.fromkeys(cleaned_words))

# 4. Main program flow
def main(input_dir: str, output_dir: str) -> Dict[str, int]:
    """Main program flow."""
    # Initialize statistics
    stats = Counter()
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Create output directory if it doesn't exist
    output_path = pathlib.Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Get input files
        input_files = get_input_files(input_dir)
        
        # Process each file with progress bar
        for file_path in tqdm(input_files, desc="Processing files"):
            # Read content
            lines = read_file_content(file_path)
            stats['total_words'] += len(lines)
            
            # Clean content
            cleaned_lines = clean_word_list(lines)
            stats['cleaned_words'] += len(cleaned_lines)
            
            # Create output file path
            output_file = output_path / f"cleaned_{file_path.name}"
            
            # Write cleaned content
            write_cleaned_content(output_file, cleaned_lines)
            stats['files_processed'] += 1
            
        return stats
        
    except Exception as e:
        logging.error(f"Error processing files: {str(e)}")
        raise

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Clean up word lists by removing numbers and standardizing format")
    parser.add_argument("input_dir", help="Directory containing input files")
    parser.add_argument("output_dir", help="Directory for cleaned output files")
    
    args = parser.parse_args()
    
    try:
        # Run main program
        stats = main(args.input_dir, args.output_dir)
        
        # Display summary
        print("\nProcessing Summary:")
        print(f"Files processed: {stats['files_processed']}")
        print(f"Total words processed: {stats['total_words']}")
        print(f"Words after cleaning: {stats['cleaned_words']}")
        print(f"Duplicates removed: {stats['total_words'] - stats['cleaned_words']}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)