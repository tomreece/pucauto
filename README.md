<p align="center"><img src="http://www.pucauto.com/img/features.png" alt="pucauto features" width="50%"/></p>

Pucauto is a PucaTrade bot that will automatically accept trades for you.

Pucauto launches Firefox, logs you in to PucaTrade, and continuously scans the
Trades page looking for bundles of trades worth more than a minimum value that
you set. If it finds one or more cards, Pucauto will accept them all for you.
All you have to do is check your Sending page and mail them out.

You can leave Pucauto running in the background of your computer while you do
other things like play Fallout 4, or sleep, or while you're at work.

### Help Support Pucauto Development

[Donate via Dwolla](https://www.dwolla.com/hub/pucauto) or
[Donate via Paypal](https://www.paypal.com/cgi-bin/webscr?business=tomreece@gmail.com&cmd=_xclick&currency_code=USD&amount=5&item_name=Pucauto)

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

The best way to stop Pucauto is with `CTRL + C` while in the Terminal window.

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

##### I'm getting a `ValueError: No JSON object could be decoded` or similar message mentioning config.json when starting Pucauto. Help!

This is usually happens because some text editors like TextEdit for Mac try to
insert smart quotes instead of normal quotes. It's a very subtle difference, but
it breaks JSON files.

Use a plain text editor like Sublime Text 2 or Notepad to edit your config file.

Also triple check for quotes around your username and password, commas at the ends
of lines, no quotes around numbers or `true` or `false`, and colons separating
the key and value.

If you still think everything is fine, you can paste your config.json into
[this site](http://jsonlint.com) and if it's valid JSON you should get a green
"Valid JSON" message at the bottom after clicking Validate.

If all else fails, delete your config.json and start over with the config.example.json
in a plain text editor as I suggested earlier.

##### How can I contact you?

[@tomreece](https://twitter.com/tomreece) or
[@pucautobot](https://twitter.com/pucautobot) or
tomreece@gmail.com

### Changelog

#### 2015-12-12 [v0.4.3](https://github.com/tomreece/pucauto/archive/v0.4.3.zip)
* Temporary disable `debug.log` due to an issue that affected Windows users. I
will look for a better long-term solution but at least now you won't see error
spam.
* Wait 5 seconds before and after turning on auto matching to be extra sure it's
on. Because if it isn't then bad things happen, like sending out lots of cards
you don't have.

#### 2015-12-09 [v0.4.2](https://github.com/tomreece/pucauto/archive/v0.4.2.zip)
* Better output when making trades. Example:
```
Found 2 card(s) worth 432 points to trade to Trader Name who has 1208 points...
  Sent Whisperwood Elemental for 254 PucaPoints!
  Failed to send Banisher Priest. Reason: Someone beat you to the draw
  Sent Greenwarden of Murasa for 178 PucaPoints!
Successfully sent 2 out of 3 cards worth 432 points!
```
* Speed improvements:
    * Immediately stop parsing a row in the trades table if the member has less
    points than the configured min_value.
    * Sum total bundle value as we go along instead of doing another pass over
    the data just to sum.
* Debugging statements logged to `debug.log` file (Thanks @Droogans)

#### 2015-12-03 [v0.4.1](https://github.com/tomreece/pucauto/archive/v0.4.1.zip)
* Most importantly, speed up bundle finding by only loading enough of the trade
list to reach a bottom member whose points exceed `min_value` in config.json
* You can now configure add on searching. See the `config.example.json` file for the new options available to you.
* Turn off add on searching all-together by setting `find_add_ons` to `false` in
config.json
* Since checking for trade add ons takes a bit of time, configure how often to
check with the `minutes_between_add_ons_check` value in config.json.
* Fix a bug where two users with the exact same name, e.g "Matt", would be
considered the same bundle recipient. Now unique profile IDs are used instead.

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
