<p align="center"><img src="http://www.pucauto.com/img/features.png" alt="pucauto features" width="50%"/></p>

Pucauto is a PucaTrade bot that will automatically accept trades for you.

Pucauto launches Firefox, logs you in to PucaTrade, and continuously scans the
Trades page looking for bundles of trades worth more than a minimum value that
you set. If it finds one or more cards, Pucauto will accept them all for you.
All you have to do is check your Sending page and mail them out.

You can leave Pucauto running in the background of your computer while you do
other things like play Fallout 4, or sleep, or while you're at work.

[Donate To Help Support Pucauto Development](https://www.dwolla.com/hub/pucauto)

### Installation

#### Prerequisites

1. Firefox
1. Python 2.7
1. Git (optional)
1. Pip (usually comes with Python)

#### Mac / Linux

1. Clone this repository with `git clone https://github.com/tomreece/pucauto.git`
 or download the [latest release](https://github.com/tomreece/pucauto/archive/master.zip).
1. Open Terminal.
1. Go to the Pucauto folder you just cloned or downloaded.
1. Run `sudo pip install -r requirements.txt` and enter your system password
when prompted.

#### Windows

1. Clone this repository with `git clone https://github.com/tomreece/pucauto.git`
 or download the [latest release](https://github.com/tomreece/pucauto/archive/master.zip).
1. Download Python 2.7.10 from https://www.python.org/downloads/
1. Install Python 2.7.10 **IMPORTANT:** Select the check box to **Add python.exe to Path**.
1. Unzip and open the Pucato folder.
1. Shift + Right-Click, then select "Open command window here".
1. Run the command `python -m pip install -r requirements.txt`

### Configuring

1. Open `config.example.json` in a plain text editor like Notepad or Sublime
 Text.
2. Enter your Pucatrade username and password in place of the default values in
 the file. Be sure to keep the quotes around the values.
3. Set the min_value to the lowest value you want Pucauto to accept. Cards or
 bundles under this value will not be traded.
4. Save the file as `config.json`, _not_ `config.example.json` or `config.json.txt`.
5. You'll get an error on startup if you forget to save as `config.json`.

### Running

After you have followed the one-time installation and configuration steps above,
you can run Pucauto with:

`python pucauto.py`

Pucauto will start running and you'll see it driving Firefox and outputting text
in the Terminal.

**IMPORTANT:** You shouldn't click things or do anything in the Firefox window that
Pucauto opens because Pucauto expects it to be in a very specific state. You can open
a new Firefox window to surf the interwebs.

### Upgrading

Pucauto is still under development and valuable new features are being added to
make trading even better. Come back to this page occasionally and check out the
Changelog at the bottom to learn about new features. If an update happens you
can upgrade by:

* If you downloaded the .zip, it's probably easiest to just move your config.json
 file to your desktop, delete your Pucauto folder and re-download the new zip.
 You don't have to follow the full installation instructions again.
* If you cloned the repository, you probably know how to use git to fetch the
 most recent changes so I'll leave it up to you.

### FAQ

##### Why do I have to provide my Pucatrade username and password? Is this safe?

Pucauto types your username and password into the proper fields on the Pucatrade
page. You can see this happening in `pucauto.py`. Your username and password are
not used for anything else. That's why this project is open source, so you can
see the code and know roughly what's happening even if you're not a developer.

##### How can I contact you?

[@tomreece](https://twitter.com/tomreece) or [@pucautobot](https://twitter.com/pucautobot) or tomreece@gmail.com

### Changelog

#### 2015-11-30 [v0.4.0](https://github.com/tomreece/pucauto/archive/v0.4.0.zip)
* Now Pucauto looks for add-on cards to any unshipped traders. This will help you
send more cards to the same recipient, saving on stamps. This makes it important
to mark your cards shipped as soon as you prepare and seal the envelope.

#### 2015-11-27 [v0.3.3](https://github.com/tomreece/pucauto/archive/v0.3.3.zip)
* Fixed a bug where Pucauto may commit to send more copies of a card than you
actually had on your Haves list.
* Add a 10 second delay after accepting trades to adhere to PucaTrade's refresh
limit.

#### 2015-11-24 [v0.3.2](https://github.com/tomreece/pucauto/archive/v0.3.2.zip)
* Use Beautiful Soup to parse the trades list to increase performance for large
trades list. The difference is very significant.

#### 2015-11-23 [v0.3.1](https://github.com/tomreece/pucauto/archive/v0.3.1.zip)
* Accept highest value cards in bundles first and fail the whole bundle if the
highest value card fails, for safety. This isn't perfect but tries to recover
from a situation where the first card is worth most of the bundle.

#### 2015-11-22 [v0.3.0](https://github.com/tomreece/pucauto/archive/v0.3.0.zip)
* Pucauto will now accept multiple lower value trades to the same user that add
up to exceed your configured min_value. This bundling helps you get rid of lots
of low value cards without wasting money on stamps.

#### 2015-10-22 [v0.2.0](https://github.com/tomreece/pucauto/archive/v0.2.0.zip)
* Username and password are now entered in `config.json` instead of as arguments
when starting the script. So now you start the bot with `python pucauto.py`
after setting the values in `config.json`.
* Added a `min_value` configuration option. Pucauto will only accept trades
above this value.
