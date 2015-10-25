# pucauto

[Donate To Help Support Pucauto Development](https://www.dwolla.com/hub/pucauto)

A Pucatrade bot that will automatically accept trades for you.

pucauto is a Python script that will launch a Firefox instance and log you in to Pucatrade. The
bot then refreshes the Trades page every 5 seconds looking for a "Send Card" button. If it finds one, it
will click the button and then complete the trade for you. You can leave pucauto running in the background of
your computer while you do other things or when you're sleeping or at work.

Now I need to build a bot to fill out envelopes...

![too-many-envelopes](http://i.imgur.com/S9ZHiO3.jpg)

### Installation

#### Prerequisites

1. Git
1. Python
1. Pip
1. Firefox

#### Mac

1. Clone this repository with `git clone https://github.com/tomreece/pucauto.git` or download the latest release
  [v0.2.0](https://github.com/tomreece/pucauto/archive/v0.2.0.zip)
1. Open Terminal.
1. Go to the pucauto folder you just cloned or downloaded.
1. Run `sudo pip install -r requirements.txt` and enter your system password when prompted.

#### Windows

1. Clone this repository with `git clone https://github.com/tomreece/pucauto.git` or download the latest release
  [v0.2.0](https://github.com/tomreece/pucauto/archive/v0.2.0.zip)
1. Download Python from https://www.python.org/downloads/
1. Install Python. **IMPORTANT:** Select the check box to associate Python with environment variables.
1. Use 7zip or WinRar to expand the archive.
1. Download Selenium from `https://pypi.python.org/pypi/selenium`. You want the file named selenium-2.48.0.tar.gz
1. Extract the archive.
1. Inside the folder you should see `setup.py`. Shift + Right-Click, then select 'Open command window here'.
1. Run the command `python setup.py install` to install Selenium

### Configuring

1. Open `config.json` in a plain text editor like Notepad or Sublime Text.
2. Enter your Pucatrade username and password in place of the default values in the file. Be sure to keep the quotes around
 the values.
3. Set the min_value to the lowest value you want the bot to accept. Cards under this value will not be traded.
4. Save `config.json`

### Running

After you have followed the one-time installation and configuration steps above, you can run pucauto with:

`python pucauto.py`

The bot will start running and you'll see it driving Firefox and outputting text in the Terminal.

### Upgrading

pucauto is still under development. So come back and check out the Changelog at the bottom of this README to learn about
new features. If an update happens you can upgrade by:

* If you downloaded the .zip, it's probably easiest to just delete your pucauto folder and re-download the new zip. You
  shouldn't have to follow the full installation instructions again.
* If you cloned the repository, you probably know how to use git to fetch the most recent changes so I'll leave it up to you.

### FAQ

* Why do I have to provide my Pucatrade username and password? Is this safe?
    * The bot types your username and password into the proper fields on the Pucatrade page. You can see this happening in
      `pucauto.py`. Your username and password are not used for anything else. That's why this project is open source, so
      you can see the code and know roughly what's happening even if you're not a developer.
* This is too difficult for me, but the bot sounds useful. Can you run it for me?
    * Yes. Check out http://www.pucauto.com/us.html then email me at tomreece@gmail.com and we'll talk.

### Help

If you have any questions, feel free to reach out to me on Twitter [@tomreece](https://twitter.com/tomreece) or tomreece@gmail.com

If the above instructions are too complicated and you are still interested in using pucauto, [let us run it for you!](http://www.pucauto.com/us.html)

### Changelog

#### 2015-10-22 [v0.2.0](https://github.com/tomreece/pucauto/archive/v0.2.0.zip)
* Username and password are now entered in `config.json` instead of as arguments when starting the script. So now you start
  the bot with `python pucauto.py` after setting the values in `config.json`.
* Added a `min_value` configuration option. pucauto will only accept trades above this value.
