#!/usr/bin/env zsh

# Exit on error, unset variable, or pipe failure
set -euo pipefail

# Create directories if they don't exist
mkdir -p ./data
mkdir -p ./logs

# Get current month and year for filtering
current_month=$(date +"%B")
current_year=$(date +"%Y")

# Generate filenames with timestamps
date_stamp=$(date -u +"%Y-%m-%d")
backupfile="shibuya-schedule-${date_stamp}.html"
textfile="shibuya-schedule-${date_stamp}.txt"
csvfile="./data/shibuya-schedule-${date_stamp}.csv"
logfile="./logs/script-execution-${date_stamp}.log"
llm_input_file="./logs/llm-input-${date_stamp}.txt"
llm_output_file="./logs/llm-output-${date_stamp}.txt"
llm_debug_script="./logs/debug-llm-${date_stamp}.sh"

# Function to log messages
log_message() {
    echo "$(date -u +"%Y-%m-%d %H:%M:%S UTC") - $1" | tee -a "$logfile"
}

# Check for required dependencies
check_dependencies() {
    log_message "Checking dependencies..."

    # Check for html2text
    if ! command -v html2text &> /dev/null; then
	log_message "html2text not found. Installing with Homebrew..."
	if ! command -v brew &> /dev/null; then
	    log_message "ERROR: Homebrew not installed. Please install Homebrew first."
	    exit 1
	fi
	brew install html2text
    fi

    # Check for llm
    if ! command -v llm &> /dev/null; then
	log_message "ERROR: 'llm' tool not found. Please install Simon Wilson's llm tool."
	exit 1
    fi

    # Check for poetry
    if ! command -v poetry &> /dev/null; then
	log_message "ERROR: poetry not found. Please install poetry."
	exit 1
    fi

    log_message "All dependencies satisfied."
}

# Download the webpage
download_webpage() {
    log_message "Downloading webpage to $backupfile..."
    if curl -s --fail https://www.shibuyahifi.com/schedule-hifi -o "$backupfile"; then
	log_message "Download successful."
    else
	log_message "ERROR: Failed to download webpage."
	exit 1
    fi
}

# Convert HTML to text
convert_to_text() {
    log_message "Converting HTML to text..."
    if html2text "$backupfile" > "$textfile"; then
	log_message "Conversion successful."
    else
	log_message "ERROR: HTML to text conversion failed."
	exit 1
    fi
}

# Create debug script for llm
create_debug_script() {
    log_message "Creating LLM debug script at $llm_debug_script"

    cat > "$llm_debug_script" << EOF
#!/usr/bin/env zsh
# Debug script for re-running LLM parsing
# Created: $(date -u)

# Get current month and year
current_month=\$(date +"%B")
current_year=\$(date +"%Y")

# This script allows you to re-run just the LLM parsing step for debugging
echo "Running llm with saved input..."
cat "$llm_input_file" | sed "s/CURRENT_MONTH/\$current_month/g" | sed "s/CURRENT_YEAR/\$current_year/g" | llm -m claude-4-sonnet > "$llm_output_file.new"

echo "\nProcessing output to extract CSV..."
if grep -q "date,artist,album,year" "$llm_output_file.new"; then
    cat "$llm_output_file.new" > "$csvfile.new"
    echo "CSV data saved to $csvfile.new"
else
    echo "ERROR: Could not find CSV header in LLM response"
    echo "Full LLM response saved to $llm_output_file.new"
fi

echo "\nComparing with previous run:"
echo "-------------------------"
echo "Differences in LLM output:"
diff "$llm_output_file" "$llm_output_file.new" || echo "Files differ"
echo "-------------------------"
echo "Differences in CSV output:"
diff "$csvfile" "$csvfile.new" || echo "Files differ"

echo "\nTo upload the new CSV file to Spotify, run:"
echo "poetry run python ./src/shibuyahifi-uploader.py --input-file $csvfile.new"

# Tips for modifying the prompt:
echo "\nTo try with a modified system prompt:"
echo "cat $textfile | llm -m claude-4-sonnet -s \"Your modified system prompt here\" > new_output.txt"
EOF

    chmod +x "$llm_debug_script"
}

# Parse text with llm to create CSV
parse_with_llm() {
    log_message "Parsing text with llm (claude-4-sonnet)..."
    log_message "Filtering for albums played in ${current_month} ${current_year}..."

    # Define the system prompt with current month and year
    system_prompt="You are parsing a file containing a listening calendar of music albums. I want to pull data out of the text I provide which was converted from html. Identify the date the album will be played on, the artist, the album, and the year of release of the album.

IMPORTANT: Only include albums that will be played in CURRENT_MONTH CURRENT_YEAR. Exclude any albums from other months.

Sort by the date the albums will be played, and not the year they were released. Remove any duplicates. Remove \"Deep Listening\" from any prefixes. Only respond with the properly formatted CSV data and nothing else. Make sure you include the CSV header line.

Format example:
date,artist,album,year
\"Wednesday Jan 1, 2025 12:30 AM\",\"Miles Davis\",\"Kind of Blue\",1959
\"Wednesday Jan 1, 2025 3:30 AM\",\"Pink Floyd\",\"Dark Side of the Moon\",1973
\"Wednesday Jan 1, 2025 5:00 AM\",\"Daft Punk\",\"Random Access Memories\",2013"

    # Save the template system prompt for debugging
    echo "$system_prompt" > "$llm_input_file"
    log_message "Saved system prompt template to $llm_input_file"

    # Replace placeholders with actual values
    actual_prompt=$(echo "$system_prompt" | sed "s/CURRENT_MONTH/$current_month/g" | sed "s/CURRENT_YEAR/$current_year/g")

    # Run llm with Claude 4 Sonnet and capture its response
    log_message "Running llm with claude-4-sonnet..."
    if cat "$textfile" | llm -m claude-4-sonnet -s "$actual_prompt" > "$llm_output_file"; then
	log_message "LLM processing successful. Full response saved to $llm_output_file"
    else
	log_message "ERROR: LLM parsing failed."
	exit 1
    fi

    # Copy the output to the CSV file (llm should already return just the CSV)
    cat "$llm_output_file" > "$csvfile"

    # Create debug script for re-running this step
    create_debug_script

    # Verify CSV has content
    if [[ ! -s "$csvfile" ]]; then
	log_message "ERROR: Generated CSV is empty."
	exit 1
    fi

    # Check if the CSV has the expected format and contains data beyond the header
    if grep -q "date,artist,album,year" "$csvfile"; then
	line_count=$(wc -l < "$csvfile")
	if [[ "$line_count" -lt 2 ]]; then
	    log_message "WARNING: CSV appears to have only a header without data. This might be normal if there are no albums scheduled for ${current_month} ${current_year}."
	else
	    log_message "CSV contains $line_count lines (including header)"
	    log_message "First few lines of CSV:"
	    head -n 5 "$csvfile" | tee -a "$logfile"
	fi
    else
	log_message "ERROR: CSV file does not contain the expected header."
	log_message "First few lines of the output:"
	head -n 5 "$csvfile" | tee -a "$logfile"
	exit 1
    fi
}

# Upload to Spotify
upload_to_spotify() {
    log_message "Uploading to Spotify..."
    if poetry run python ./src/shibuyahifi-uploader.py --input-file "$csvfile"; then
	log_message "Spotify upload successful."
    else
	log_message "ERROR: Spotify upload failed."
	exit 1
    fi
}

# Cleanup temporary files
cleanup() {
    log_message "Cleaning up temporary files..."
    # Only remove the HTML and text files, keep logs and debug files
    rm -f "$backupfile" "$textfile"
    log_message "Cleanup complete. Kept debug files for troubleshooting."
    log_message "To debug LLM parsing, run: $llm_debug_script"
}

# Main execution
main() {
    # Check if a specific step was requested
    if [[ $# -gt 0 ]]; then
	case "$1" in
	    --parse-only)
		log_message "Running parse-only mode (assuming files exist)"
		parse_with_llm
		;;
	    --help)
		echo "Usage: $0 [OPTION]"
		echo "Options:"
		echo "  --parse-only    Run only the LLM parsing step (assumes text file exists)"
		echo "  --help          Show this help message"
		exit 0
		;;
	    *)
		echo "Unknown option: $1"
		echo "Use --help for usage information"
		exit 1
		;;
	esac
    else
	# Run the full process
	log_message "Starting Shibuya HiFi album scraper and Spotify uploader"
	log_message "Targeting albums for ${current_month} ${current_year}"

	check_dependencies
	download_webpage
	convert_to_text
	parse_with_llm
	upload_to_spotify
	cleanup

	log_message "All tasks completed successfully."
    fi
}

# Run the main function with all arguments passed to the script
main "$@"
