# IMS

IMS is a project designed to manage inventory systems efficiently.

## Prerequisites

- Python 3.x
- pip (Python package installer)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/FlameDoesVC/ims.git
   ```
2. Navigate to the project directory:
   ```sh
   cd ims
   ```
3. Create a virtual environment:
   ```sh
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```sh
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```
5. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

IMS will be useful in managing inventory for a tech shop by providing the following features:

- **Product Management**: Easily add, update, and remove products from the inventory.
- **Stock Tracking**: Keep track of stock levels for each product, ensuring that you never run out of essential items.
- **Sales Recording**: Record sales transactions to keep an accurate log of sold items and update stock levels accordingly.
- **Reporting**: Generate reports on inventory status, sales performance, and stock levels to make informed business decisions.

## End-to-End Testing

Simulate real user scenarios and test the application from start to finish. Use tools like `pytest` with plugins such as `pytest-console-scripts` to test CLI commands.

Example:

````python
def test_cli_command(script_runner):
    ret = script_runner.run('your_cli_command', 'arg1', 'arg2')
    assert ret.success
    assert 'expected_output' in ret.stdout
````