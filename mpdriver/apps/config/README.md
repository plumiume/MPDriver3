## 1. Overview of `mpdriver config`
Explain that `mpdriver config` is uselocal, **gglobal,system, anddefault.

## 2. Command Structure and
Specify that each configuration level is exclusive and prioritized as:

`--local` (project-specific),
`--global` (user-specific),
`--system` (system-wide),
`--default` (fallback configuration).
The tool processes configuration options in this strict priority. If multiple options are passed, it will prioritize the highest-ranking option among them.

### Key Setting Format
Since `key` values use JSON-like syntax, you might include examples such as:

- `mpdriver config --local "database.connection.timeout" 30`
- `mpdriver config --global "logging.level" "DEBUG"`

Keys are structured as JSON-like paths to specify nested configurations, so a `.` in the key signifies a hierarchical level, similar to JSON object structure.

## 3. Flag and Functionality Descriptions
Here’s how you could describe each option:

- `--local`, `--global`, `--system`, `--default`: Selects the configuration level.
- `key`: Required. The configuration item, accessed with JSON-style key names, e.g., "database.connection.timeout".
- `value`: Optional. The value to set for the specified key. If omitted, the current value for `key` is retrieved.
- `-v`, `--verbose`: Enables verbose output for diagnostic details (planned for future detail enhancements).
- `-y`, `--yes`: Automatically confirms all prompts, bypassing user confirmation.

## 4. Error Handling and Warnings
Add that:

- If an invalid key is specified, the program raises an error due to the missing default file.
- Permission escalation is not required; users will not be prompted for elevated permissions, even at the system level.

## 5. Examples and Usage Scenarios
Include common examples, such as:

- **Setting a Value Locally**:

```bash
mpdriver config --local mediapipe.holistic.static_image_mode true
```
- **Retrieving a Global Value**:

```bash
mpdriver config --global mediapipe.holistic.static_image_mode
```
- **Copying Settings (placeholder functionality)**:

```bash
mpdriver config --global --copy
```
- **Deleting a Configuration (placeholder functionality)**:

```bash
mpdriver config --global -d mediapipe.holistic.static_image_mode
```
## 6. Configuration File Format and Future Development
Mention that:

- The configuration is stored in JSON format, allowing straightforward editing for advanced users.
- While the mpdriver config tool does not currently allow users to modify the location of the configuration files, future enhancements may expand this flexibility.