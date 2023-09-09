
## Documentation

This repo creates an order book for ethereum prices on the dxdy exchange. In addition to keeping a well updated order book the terminal will; print out the best bid & its size, best ask & its size, as well as the spread. If any of these values change, the terminal will print out an update. This kind of system logic in Rust or C++ languages can be used for market making, but in python it is great for pricing research, and getting a greater understanding of how DeFi exchanges work.


### Updates Bids



### Updated Asks



### Spread


## How to Use This Project

Follow the steps below to set up and run this project locally:

1. **Download Repo**

2. **Navigate to Project Directory**: Move into the project directory via the command line.

3. **Download requirements file in /python**:
    ```
    pip install -r requirements.txt
    ```

4. **Start the Server**: STrat the oder book
    ```
    python3 order_jag.py
    ```