from flask import Flask, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Grid Input (Numbers Only)</title>
    <style>
        body { font-family: sans-serif; }
        .grid-container {
            width: 100vw;
            max-width: 100vw;
            height: 80vh;
            max-height: 80vh;
            margin-left: 0;
            margin-right: 0;
            margin-top: 0;
            margin-bottom: 1em;
            background: #fafafa;
            border-radius: 8px;
            box-shadow: 0 2px 8px #0001;
            padding: 8px 8px 8px 32px;
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            overflow: auto;
        }
        .responsive-table-wrapper {
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            overflow: auto;
        }
        .responsive-table {
            display: inline-block;
            width: auto;
            height: auto;
            max-width: 100vw;
            max-height: 70vh;
            overflow: auto;
        }
        table {
            border-collapse: separate;
            border-spacing: 0;
            margin-left: 0;
            margin-right: 0;
            width: auto;
            height: auto;
            overflow: auto;
        }
        td {
            border: 1px solid #333;
            width: 72px; height: 72px;
            min-width: 72px; min-height: 72px;
            max-width: 72px; max-height: 72px;
            aspect-ratio: 1 / 1;
            text-align: center; position: relative; padding: 0; background: #fff;
            font-size: 2.2em;
            box-sizing: border-box;
        }
        td input[type="text"] {
            width: 100%;
            height: 100%;
            font-size: inherit;
            text-align: center;
            border: none;
            outline: none;
            background: transparent;
            box-sizing: border-box;
        }
        .target-col {
            border-right: 3px solid #333 !important;
            background-color: #f0e6ff !important;
        }
        .spacer {
            width: 20px;
            background: none;
            border: none;
        }
        .up-arrow-col {
            background-color: #fffbe6;
        }
        input[type="text"] {
            width: 100%; height: 100%;
            text-align: center; font-weight: bold;
            background: transparent !important;
            border: none; outline: none;
            font-size: 2em;
        }
        input[type="text"]:focus {
            box-shadow: 0 0 0 3px #ff9800;
            border: 2px solid #ff9800;
        }
        @media (max-width: 1200px), (max-height: 900px) {
            td { width: 48px; height: 48px; min-width: 48px; min-height: 48px; max-width: 48px; max-height: 48px; aspect-ratio: 1 / 1; font-size: 1.5em; }
        }
        @media (max-width: 900px), (max-height: 700px) {
            td { width: 32px; height: 32px; min-width: 32px; min-height: 32px; max-width: 32px; max-height: 32px; aspect-ratio: 1 / 1; font-size: 1.1em; }
        }
        @media (max-width: 600px), (max-height: 500px) {
            td { width: 20px; height: 20px; min-width: 20px; min-height: 20px; max-width: 20px; max-height: 20px; aspect-ratio: 1 / 1; font-size: 0.8em; }
        }
    </style>
    <script>
    function setupGridInputs() {
        const upArrowInputs = Array.from(document.querySelectorAll('.up-arrow-col input[type="text"]'));
        function updateUpArrowInventory() {
            // Count number of 5s in grid/target cells
            let used = 0;
            document.querySelectorAll('td:not(.up-arrow-col) input[type="text"]').forEach(input => {
                if (input.value === '5') used++;
            });
            // Set up arrow inventory
            upArrowInputs.forEach((input, idx) => {
                input.value = idx < (upArrowInputs.length - used) ? '5' : '';
            });
        }
        document.querySelectorAll('input[type="text"]').forEach((input) => {
            input.addEventListener('focus', function() {
                this.select();
            });
            input.addEventListener('mousedown', function(e) {
                e.preventDefault();
                this.focus();
                this.select();
            });
            input.addEventListener('keydown', function(e) {
                // Arrow key navigation
                const td = this.parentElement;
                const tr = td.parentElement;
                const table = tr.parentElement;
                const colIdx = Array.from(tr.children).indexOf(td);
                const isTarget = td.classList.contains('target-col');
                if (e.key === 'Tab') {
                    e.preventDefault();
                    if (isTarget) {
                        // Move to next target input in the same row
                        let nextTd = td.nextElementSibling;
                        while (nextTd && !nextTd.classList.contains('target-col')) {
                            nextTd = nextTd.nextElementSibling;
                        }
                        if (nextTd) {
                            const nextInput = nextTd.querySelector('input[type="text"]');
                            if (nextInput) nextInput.focus();
                        } else {
                            // If at end of target columns, go to first target in next row
                            const nextRow = tr.nextElementSibling;
                            if (nextRow) {
                                const firstTarget = Array.from(nextRow.querySelectorAll('td.target-col input[type="text"]'))[0];
                                if (firstTarget) firstTarget.focus();
                            }
                        }
                    } else {
                        // For grid cells, tab moves right, unless at end of row, then down
                        let nextTd = td.nextElementSibling;
                        // Skip spacers and up-arrow columns
                        while (nextTd && (nextTd.classList.contains('spacer') || nextTd.classList.contains('up-arrow-col'))) {
                            nextTd = nextTd.nextElementSibling;
                        }
                        if (nextTd) {
                            const nextInput = nextTd.querySelector('input[type="text"]');
                            if (nextInput) nextInput.focus();
                        } else {
                            // If at end of row, go to first grid cell in next row
                            const nextRow = tr.nextElementSibling;
                            if (nextRow) {
                                // Find first grid cell (not target, not spacer, not up-arrow)
                                for (let k = 0; k < nextRow.children.length; k++) {
                                    const cell = nextRow.children[k];
                                    if (!cell.classList.contains('target-col') && !cell.classList.contains('spacer') && !cell.classList.contains('up-arrow-col')) {
                                        const nextInput = cell.querySelector('input[type="text"]');
                                        if (nextInput) {
                                            nextInput.focus();
                                            break;
                                        }
                                    }
                                }
                            }
                        }
                    }
                    return;
                }
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextRow = tr.nextElementSibling;
                    if (nextRow) {
                        const nextTd = nextRow.children[colIdx];
                        if (nextTd) {
                            const nextInput = nextTd.querySelector('input[type="text"]');
                            if (nextInput) nextInput.focus();
                        }
                    }
                    return;
                }
                if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevRow = tr.previousElementSibling;
                    if (prevRow) {
                        const prevTd = prevRow.children[colIdx];
                        if (prevTd) {
                            const prevInput = prevTd.querySelector('input[type="text"]');
                            if (prevInput) prevInput.focus();
                        }
                    }
                    return;
                }
                if (e.key === 'ArrowLeft') {
                    e.preventDefault();
                    const prevTd = td.previousElementSibling;
                    if (prevTd) {
                        const prevInput = prevTd.querySelector('input[type="text"]');
                        if (prevInput) prevInput.focus();
                    }
                    return;
                }
                if (e.key === 'ArrowRight') {
                    e.preventDefault();
                    const nextTd = td.nextElementSibling;
                    if (nextTd) {
                        const nextInput = nextTd.querySelector('input[type="text"]');
                        if (nextInput) nextInput.focus();
                    }
                    return;
                }
                // Enter key navigation
                if (e.key === 'Enter') {
                    e.preventDefault();
                    const nextRow = tr.nextElementSibling;
                    if (nextRow) {
                        const nextTd = nextRow.children[colIdx];
                        if (nextTd) {
                            const nextInput = nextTd.querySelector('input[type="text"]');
                            if (nextInput) nextInput.focus();
                        }
                    }
                    return;
                }
                // Only allow 0-4 for target columns, 0-5 for grid cells
                if (isTarget) {
                    if (!/^[0-4]$/.test(e.key)) {
                        e.preventDefault();
                        return;
                    }
                } else {
                    if (!/^[0-5]$/.test(e.key)) {
                        e.preventDefault();
                        return;
                    }
                }
                e.preventDefault();
                const prev = this.value;
                this.value = e.key;
                this.select();
                // Update up arrow inventory if 5 is added/removed
                if (!isTarget && ((prev !== '5' && e.key === '5') || (prev === '5' && e.key !== '5'))) {
                    updateUpArrowInventory();
                }
            });
            input.addEventListener('input', function() {
                // Update up arrow inventory if 5 is added/removed
                updateUpArrowInventory();
            });
        });
        // Initial inventory update
        updateUpArrowInventory();
    }
    window.addEventListener('DOMContentLoaded', setupGridInputs);
    </script>
</head>
<body>
    <h2>Enter Grid Size</h2>
    <form method="post" action="/grid" style="margin-bottom: 1em;">
        <label style="display:inline-block; margin-right:8px;">Rows:
            <input type="number" name="rows" min="1" max="16" value="8" required style="width:60px; display:inline-block;">
        </label>
        <label style="display:inline-block; margin-right:8px;">Columns:
            <input type="number" name="cols" min="1" max="16" value="8" required style="width:60px; display:inline-block;">
        </label>
        <label style="display:inline-block; margin-right:8px;">Target Columns:
            <select name="target_cols" style="width:60px; display:inline-block;">
                <option value="1">1</option>
                <option value="2" selected>2</option>
            </select>
        </label>
        <label style="display:inline-block; margin-right:8px;">Up Arrows:
            <input type="number" name="up_arrows" min="0" value="8" required style="width:60px; display:inline-block;">
        </label>
        <button type="submit" style="display:inline-block;">Create Grid</button>
    </form>
    {% if grid %}
    <h2>Enter Tiles (0-4 for target columns, 0-5 for grid, 5 for up arrow inventory)</h2>
    <form method="post" action="/submit">
        <input type="hidden" name="rows" value="{{rows}}">
        <input type="hidden" name="cols" value="{{cols}}">
        <input type="hidden" name="target_cols" value="{{target_cols}}">
        <input type="hidden" name="up_arrows" value="{{up_arrows}}">
        <button type="submit" style="margin-bottom: 1em;">Submit Grid</button>
        <div class="grid-container">
            <div class="responsive-table-wrapper">
                <div class="responsive-table" style="display: flex; align-items: flex-end;">
                    <table style="vertical-align: bottom;">
                        {% set up_arrow_cols = (up_arrows // rows) + (1 if up_arrows % rows else 0) %}
                        {% for i in range(rows) %}
                            <tr>
                            {% for t in range(target_cols) %}
                                <td class="target-col">
                                    <input type="text" name="target_{{i}}_{{t}}" maxlength="1" value="0" required autocomplete="off" pattern="[0-4]">
                                </td>
                            {% endfor %}
                            <td class="spacer"></td>
                            {% for j in range(cols) %}
                                <td>
                                    <input type="text" name="cell_{{i}}_{{j}}" maxlength="1" value="0" required autocomplete="off">
                                </td>
                            {% endfor %}
                            <td class="spacer"></td>
                            {% for c in range(up_arrow_cols) %}
                                {% set up_arrow_idx = c * rows + i %}
                                {% if up_arrow_idx < up_arrows %}
                                    <td class="up-arrow-col">
                                        <input type="text" name="up_arrow_{{up_arrow_idx}}" maxlength="1" value="5" required autocomplete="off" readonly>
                                    </td>
                                {% else %}
                                    <td class="up-arrow-col"></td>
                                {% endif %}
                            {% endfor %}
                            </tr>
                        {% endfor %}
                    </table>
                </div>
            </div>
        </div>
    </form>
    {% endif %}
</body>
</html>
'''

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE, grid=False)

@app.route('/grid', methods=['POST'])
def grid():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    target_cols = int(request.form.get('target_cols', 1))
    up_arrows = int(request.form.get('up_arrows', 8))
    return render_template_string(HTML_TEMPLATE, grid=True, rows=rows, cols=cols, target_cols=target_cols, up_arrows=up_arrows)

@app.route('/submit', methods=['POST'])
def submit():
    rows = int(request.form['rows'])
    cols = int(request.form['cols'])
    target_cols = int(request.form.get('target_cols', 1))
    up_arrows = int(request.form.get('up_arrows', 8))
    grid = []
    target_grid = []
    up_arrow_inventory = []
    for i in range(rows):
        t_row = []
        for t in range(target_cols):
            val_str = request.form.get(f'target_{i}_{t}', '0')
            val = int(val_str) if val_str and val_str.isdigit() else 0
            t_row.append(val)
        target_grid.append(t_row)
        row = []
        for j in range(cols):
            val_str = request.form.get(f'cell_{i}_{j}', '0')
            val = int(val_str) if val_str and val_str.isdigit() else 0
            row.append(val)
        grid.append(row)
    for idx in range(up_arrows):
        val_str = request.form.get(f'up_arrow_{idx}', '5')
        val = int(val_str) if val_str and val_str.isdigit() else 5
        up_arrow_inventory.append(val)
    # Save grid data to a file (append as JSON)
    import json
    import os
    grid_data = {
        "target_grid": target_grid,
        "main_grid": grid,
        "up_arrow_inventory": up_arrow_inventory
    }
    grids_file = os.path.join(os.path.dirname(__file__), "grids.json")
    # Read existing data
    try:
        with open(grids_file, "r") as f:
            all_grids = json.load(f)
    except Exception:
        all_grids = []
    all_grids.append(grid_data)
    with open(grids_file, "w") as f:
        json.dump(all_grids, f, indent=2)
    # Show result
    result_html = '<h2>Saved Grids</h2>'
    result_html += '<b>Target Grid:</b><pre>' + str(target_grid) + '</pre>'
    result_html += '<b>Main Grid:</b><pre>' + str(grid) + '</pre>'
    result_html += '<b>Up Arrow Inventory:</b><pre>' + str(up_arrow_inventory) + '</pre>'
    result_html += '<br><a href="/">Back</a>'
    return result_html

if __name__ == '__main__':
    app.run(debug=True)
