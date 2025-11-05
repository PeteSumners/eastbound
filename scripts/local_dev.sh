#!/bin/bash
# Local development helper script
# Makes common tasks easier when developing locally

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper function
print_header() {
    echo -e "${BLUE}===================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}===================================${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

# Main menu
show_menu() {
    clear
    print_header "EASTBOUND LOCAL DEVELOPMENT"
    echo
    echo "1) Test setup (verify configuration)"
    echo "2) Create new draft"
    echo "3) Preview draft (dry run)"
    echo "4) Publish to Substack (dry run)"
    echo "5) Generate Twitter thread (dry run)"
    echo "6) List all drafts"
    echo "7) List scheduled posts"
    echo "8) List published posts"
    echo "9) Install/update dependencies"
    echo "0) Exit"
    echo
    read -p "Choose an option: " choice

    case $choice in
        1) test_setup ;;
        2) create_draft ;;
        3) preview_draft ;;
        4) publish_draft ;;
        5) generate_thread ;;
        6) list_drafts ;;
        7) list_scheduled ;;
        8) list_published ;;
        9) install_deps ;;
        0) exit 0 ;;
        *) print_error "Invalid option"; sleep 2; show_menu ;;
    esac
}

test_setup() {
    print_header "Testing Setup"
    python3 scripts/test_setup.py
    read -p "Press Enter to continue..."
    show_menu
}

create_draft() {
    print_header "Create New Draft"
    echo
    echo "Choose content type:"
    echo "1) Weekly Analysis"
    echo "2) Translation"
    read -p "Type (1 or 2): " type_choice

    case $type_choice in
        1) content_type="weekly-analysis" ;;
        2) content_type="translation" ;;
        *) print_error "Invalid choice"; sleep 2; show_menu; return ;;
    esac

    read -p "Title: " title

    if [ "$content_type" == "translation" ]; then
        read -p "Original URL (optional): " url
    fi

    read -p "Schedule days from now (optional, press Enter for today): " schedule_days

    cmd="python3 scripts/create_draft.py --type $content_type --title \"$title\""

    if [ -n "$url" ]; then
        cmd="$cmd --original-url \"$url\""
    fi

    if [ -n "$schedule_days" ]; then
        cmd="$cmd --schedule-days $schedule_days"
    fi

    echo
    print_header "Creating Draft"
    eval $cmd

    read -p "Press Enter to continue..."
    show_menu
}

preview_draft() {
    print_header "Preview Draft"
    list_files "content/drafts"
    read -p "Enter filename: " filename

    if [ -f "content/drafts/$filename" ]; then
        echo
        print_header "Draft Preview"
        cat "content/drafts/$filename" | head -50
        echo
        print_warning "Showing first 50 lines only"
    else
        print_error "File not found"
    fi

    read -p "Press Enter to continue..."
    show_menu
}

publish_draft() {
    print_header "Test Publish (Dry Run)"
    list_files "content/drafts"
    read -p "Enter filename: " filename

    if [ -f "content/drafts/$filename" ]; then
        echo
        python3 scripts/publish_to_substack.py --file "content/drafts/$filename" --dry-run
    else
        print_error "File not found"
    fi

    read -p "Press Enter to continue..."
    show_menu
}

generate_thread() {
    print_header "Generate Twitter Thread (Dry Run)"

    echo "Choose directory:"
    echo "1) Drafts"
    echo "2) Published"
    read -p "Directory (1 or 2): " dir_choice

    case $dir_choice in
        1) dir="content/drafts" ;;
        2) dir="content/published" ;;
        *) print_error "Invalid choice"; sleep 2; show_menu; return ;;
    esac

    list_files "$dir"
    read -p "Enter filename: " filename

    if [ -f "$dir/$filename" ]; then
        echo
        python3 scripts/post_to_twitter.py --file "$dir/$filename" --dry-run
    else
        print_error "File not found"
    fi

    read -p "Press Enter to continue..."
    show_menu
}

list_drafts() {
    print_header "Drafts"
    list_files "content/drafts"
    read -p "Press Enter to continue..."
    show_menu
}

list_scheduled() {
    print_header "Scheduled Posts"
    list_files "content/scheduled"
    read -p "Press Enter to continue..."
    show_menu
}

list_published() {
    print_header "Published Posts"
    list_files "content/published"
    read -p "Press Enter to continue..."
    show_menu
}

list_files() {
    dir=$1
    if [ -d "$dir" ]; then
        files=$(ls -1 "$dir"/*.md 2>/dev/null || echo "")
        if [ -n "$files" ]; then
            echo "$files" | while read file; do
                filename=$(basename "$file")
                print_success "$filename"
            done
        else
            print_warning "No files found in $dir"
        fi
    else
        print_warning "Directory $dir does not exist"
    fi
}

install_deps() {
    print_header "Installing Dependencies"
    pip3 install -r requirements.txt
    print_success "Dependencies installed"
    read -p "Press Enter to continue..."
    show_menu
}

# Start the menu
show_menu
