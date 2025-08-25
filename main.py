# main.py
from fasthtml.common import *
from fasthtml.fastapp import fast_app
import uvicorn

app, rt = fast_app()

# JavaScript with a dynamic popup notification system
js_code = """
    let fileHandle; // This will store the handle to the opened file

    // MODIFIED FUNCTION to create and remove a popup dynamically
    function showTemporaryMessage(message) {
        // 1. Create a new div element for the popup
        const popup = document.createElement('div');
        popup.textContent = message;

        // 2. Style the popup dynamically using JavaScript
        Object.assign(popup.style, {
            position: 'fixed',
            top: '20px',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: '#4CAF50',
            color: 'white',
            padding: '15px',
            borderRadius: '8px',
            zIndex: '1000',
            transition: 'opacity 0.5s ease-out',
            opacity: '1'
        });

        // 3. Add the popup to the page's body
        document.body.appendChild(popup);

        // 4. Set a timer to fade out and then remove the popup
        setTimeout(() => {
            popup.style.opacity = '0';
            // Wait for the fade-out transition to finish before removing the element
            setTimeout(() => {
                document.body.removeChild(popup);
            }, 500); // This duration must match the CSS transition time
        }, 2000); // The popup stays visible for 2 seconds
    }

    async function openFile() {
        try {
            [fileHandle] = await window.showOpenFilePicker();
            
            if (fileHandle) {
                const file = await fileHandle.getFile();
                const contents = await file.text();
                
                const textArea = document.getElementById('editor');
                const saveButton = document.getElementById('save-button');
                const reloadButton = document.getElementById('reload-button');
                const statusDiv = document.getElementById('status');

                textArea.value = contents;
                textArea.disabled = false;
                saveButton.disabled = false;
                reloadButton.disabled = false;
                statusDiv.textContent = `Editing: ${file.name}`;
            }
        } catch (err) {
            console.error('Error opening file:', err);
            if (err.name !== 'AbortError') {
                alert("Could not open file. See console for details.");
            }
        }
    }

    async function saveFile() {
        if (!fileHandle) {
            alert('No file is open to save.');
            return;
        }

        try {
            const textArea = document.getElementById('editor');
            const newContent = textArea.value;

            const writable = await fileHandle.createWritable();
            await writable.write(newContent);
            await writable.close();
            
            showTemporaryMessage('File saved successfully!');
        } catch (err) {
            console.error('Error saving file:', err);
            alert('Could not save file. See console for details.');
        }
    }

    async function reloadFile() {
        if (!fileHandle) {
            alert('No file is open to reload.');
            return;
        }

        try {
            const file = await fileHandle.getFile();
            const contents = await file.text();
            document.getElementById('editor').value = contents;

            showTemporaryMessage('File content has been reloaded from disk.');
        } catch (err) {
            console.error('Error reloading file:', err);
            alert('Could not reload file. It may have been moved or deleted.');
        }
    }
"""


@rt("/")
def get():
    # The static notification Div has been removed from the HTML structure
    main_layout = (
        Title("Direct File Editor"),
        H1("Open, Edit, and Sync a Local File"),
        P(
            "Select a text file, modify its content, and save it back or reload from disk."
        ),
        Div(
            Button("1. Open File", onclick="openFile()"),
            Button(
                "2. Reload from File",
                id="reload-button",
                onclick="reloadFile()",
                disabled=True,
            ),
            Button(
                "3. Save Changes", id="save-button", onclick="saveFile()", disabled=True
            ),
            style="display: flex; gap: 10px;",
        ),
        Hr(),
        Div(id="status", style="font-style: italic; margin-bottom: 10px;"),
        Textarea(
            id="editor",
            rows=20,
            style="width: 90%; font-family: monospace;",
            placeholder="Open a file to see its content here...",
            disabled=True,
        ),
        Script(js_code),
    )

    compatibility_check = (
        Div(
            H2("Browser Not Supported"),
            P(
                "This feature requires a browser with the File System Access API, "
                "such as Google Chrome or Microsoft Edge."
            ),
            id="compatibility-warning",
            style=(
                "display: none; position: fixed; top: 0; left: 0; width: 100%; "
                "height: 100%; background-color: rgba(0,0,0,0.8); color: white; "
                "text-align: center; padding-top: 20%; z-index: 2000;"
            ),
        ),
        Script(
            """
            if (!window.showOpenFilePicker) {
                document.getElementById('compatibility-warning').style.display = 'block';
            }
            """
        ),
    )

    return main_layout + compatibility_check


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
