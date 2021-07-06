# Japanese Card Randomizer for Anki
# Downloading
Download from AnkiWeb https://ankiweb.net/shared/info/1476821676
# Building
Building the .ankiaddon can be done on Windows by running `build.bat`
On Linux there currently isn't a one click build setup, but all that needs to be done is to zip everything except for `meta.json`(it may not exist) into a `.zip` file, and then rename to a `.ankiaddon` file
# What does this do?
This addon has two main features.
1. Font Randomizer: Randomly changes fonts every time you review a card (starts with 2 extra fonts). 
   * This helps deal with the problem of failing to recognize a kanji in fonts outside of the one you use in Anki by not letting your brain just remember the way that kanji looks in one specific font.
2. Katakana Converter: Randomly (for the entire page) swap hiragana with katakana and katakana with hiragana.
   * This helps train your katakana reading speed by randomly giving you sentences. 
   * For example `リンゴが好きです` will sometimes (by default 50% of the time) convert to `りんごガ好キデス`
   * Since it not entirely hiragana or entirely katakana it is still readable. You can tell where words start and end still.
3. Vertical Text: (Disabled by default) Randomly displays the card in a vertical text format instead of horizonal
   * This is for extra practice reading vertical text. If your immersion doesn't include vertical text it can be tough to read sometimes.
   * NOTE: This feature requires you to mark what section of your card is your expression field by adding the class name `expression-field` to it. For example, if you edit your card and see something like `<div class="question">{{Expression}}</div>` you just need to add `expression-field` to the class list like so `<div class="question expression-field">{{Expression}}</div>`. The `{{Expression}}` part might be different, it's just the name of the first field of your card.

# Setup
After installing the addon through the anki web addon page the addon will be enabled by default. Simply start reviewing cards and fonts will be randomized along with katakana and hiragana being randomly swapped.

# Configuration
The addon can be configured by going to Tools->Add-ons, Selecting JapaneseCardRandomizer, then selecting Config
Below are what each config value does

* `limitedToTheseDecks` Every sub section has a the ability to limit it to only certain deck names. Please note that the true deck name might differ from what's displayed visually. To get the correct deck name click the options/gear icon and click "rename" and copy the text
* `globalDeckLimitation` This is for convenience if you just want all the features enabled but only for certain decks. This saves you having to enter the deck name in the `limitedToTheseDecks` for every option. 
    * Note: For a feature to be enabled the card must be apart of a deck in the `globalDeckLimitation` AND `limitedToTheseDecks` for that feature.  So if you have a global deck limit of `["Deck A"]` and the font randomizer has a deck limit of `["Deck B"]`, then Deck A will not have the font randomizer enabled, because the global deck limiter restricts that.

* `katakanaConverter`  This feature swaps all hiragana and katakana around to allow for some extra katakana reading practice.
    *  `chance` Controls the percent chance to swap all hiragana and katakana. 
        * 0 is off, 1 is always swap, 0.5 is 50% chance. Any value between 0 and 1 works.
* `fontRandomizer` Switches randomly between a set of selected fonts
     * `fontsToRandomlyChoose` A list of what fonts to randomly change to. The fonts you enter in `fontsToRandomlyChoose`  **MUST** be in your `/collections.media` folder in anki. Format `["A.tff", "B.tff", "C.tcc"]`
     * NOTE: Do not include your default font in this. It will choose between the fonts in this list AND the one you have on your card already. For example if you want to choose from fonts `A.tff`, `B.tff`, and `C.tff`, and the font on your card is already `A.tff` then `fontsToRandomlyChoose` should be `["B.tff", "C.tff"]`
    * Fonts `"_hgrkk.ttf"` and `"_yugothb.ttc"` are included by default for convenience
 
 * `verticalText` Switches the card to layout text in a vertical left to right fashion, just like light novels are displayed. This is for vertical text reading practice
    * `chance` The chance to convert to vertical text. NOTE: This is set to `0` by default.
    * NOTE: This feature requires you to mark what section of your card is your expression field by adding the class name `expression-field` to it. For example, if you edit your card and see something like `<div class="question">{{Expression}}</div>` you just need to add `expression-field` to the class list like so `<div class="question expression-field">{{Expression}}</div>`
    * This feature may mess with your layout in unexpected ways (although it's only temporary). If you run into issues after turning it on, set it back to 0 and let me know what went wrong through a github issue https://github.com/Toocanzs/AnkiJapaneseCardRandomizer/issues/new


The process for adding a new font goes as follows:
1. Download a font, for the sake of example we'll call it `myfont.tff`, and copy it to the `/collections.media` folder of your Anki install.
2. Open the config for the Card Randomizer addon and add your font to the list of fonts. For example if the list already has `"fontsToRandomlyChoose": ["_hgrkk.ttf", "_yugothb.ttc"]` you just need to add your font to the end like so: `"fontsToRandomlyChoose": ["_hgrkk.ttf", "_yugothb.ttc", "myfont.tff"]`

Disabling katakana conversion can be done by setting `percentChanceToConvertToKatakana` to 0, and disabling font randomization can be done by setting `fontsToRandomlyChoose` to `[]`

# Licence
This addon is shares the same licence as Anki (GNU Affero General Public License 3).
