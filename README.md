# pucauto

A tool to help you automatically check for and accept trades on pucatrade.com.

pucauto is a Python script that uses Selenium to launch a Firefox instance and log you in to Pucatrade. The
script then refreshes the Trades page every 5 seconds looking for a "Send Card" button. If it finds one, it
will click the button and then complete the trade for you. You can leave pucauto running in the background of
your computer while you do other things or when you're sleeping or at work.

### Installation

#### Prerequisites

1. Git
2. Python
3. Pip
4. Firefox

Most Macs come with most of this stuff already installed. If you're on Windows, I'm not sure what to do. Can someone
contribute to this repo and help me write some Windows instructions?

#### Steps

1. Open Terminal
2. Clone this repository with `git clone https://github.com/tomreece/pucauto.git`
3. Run `cd pucauto`
3. Run `pip install -r requirements.txt`

### Running

After you have followed the installation steps, you can run pucauto with:

`python pucauto.py youremailaddress@gmail.com yourpucatradepassword`

### Help

If you have any questions, feel free to reach out to me on Twitter @tomreece
