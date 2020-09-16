# Grader SDA Moodle Plugin

Just change what you want. But if you need to change the JS file, you need to
copy all `amd/src/*.js` folder to `amd/build/*.js` or run `copy.sh`.

## Installation

1. Zip the folder and upload via moodle plugin site admin page.
1. Open `config.php` and add `grader_url` and `grader_token`. Do not add trailing slash to URL.
   ```
   $CFG->grader_url = '<grader_url>';
   $CFG->grader_token = '<grader_token>';
   ```
