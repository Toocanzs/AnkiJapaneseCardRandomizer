# Japanese Card Randomizer for Anki

# What does this do?
This addon has two main features.
1. Randomly changing fonts every time you review a card. 
   * This helps deal with the problem of failing to recognize a kanji in fonts outside of the one you use in Anki by not letting your brain just remember the way that kanji looks in one specific font.
3. Randomly (for the entire page) swap hiragana with katakana and katakana with hiragana.
   * This helps train your katakana reading speed by randomly giving you sentences. 
   * For example `リンゴが好きです` will sometimes (by default 50% of the time) convert to `りんごガ好キデス`
   * Since it not entirely hiragana or entirely katakana it is still readable. You can tell where words start and end still.

# Setup
After installing the addon through the anki web addon page the addon will be enabled by default. Simply start reviewing cards and fonts will be randomized along with katakana and hiragana being randomly swapped.

# Configuration
The addon can be configured by going to Tools->Add-ons, Selecting JapaneseCardRandomizer, then selecting Config
Below are what each config value does
* `percentChanceToConvertToKatakana` Controls the percent chance to swap all hiragana and katakana. 0 is off, 1 is always swap, 0.5 is 50% chance. Any value between 0 and 1 works.
* `fontsToRandomlyChoose` A list of what fonts to randomly change to. The fonts you enter in `fontsToRandomlyChoose` **MUST** be in your `/collections.media` folder in anki. Format `["A.tff", "B.tff", "C.tcc"]`
NOTE: Do not include you're default font in this. It will choose between the fonts in this list AND the one you have on your card already. For example if you want to choose from fonts `A.tff`, `B.tff`, and `C.tff`, and the font on your card is already `A.tff` then `fontsToRandomlyChoose` should be `["B.tff", "C.tff"]`
Fonts `"_hgrkk.ttf"` and `"_yugothb.ttc"` are included by default for convenience 

The process for adding a new font goes as follows:
1. Download a font, for the sake of example we'll call it `myfont.tff`, and copy it to the `/collections.media` folder of your Anki install.
2. Open the config for the Card Randomizer addon and add your font to the list of fonts. For example if the list already has `"fontsToRandomlyChoose": ["_hgrkk.ttf", "_yugothb.ttc"]` you just need to add your font to the end like so: `"fontsToRandomlyChoose": ["_hgrkk.ttf", "_yugothb.ttc", "myfont.tff"]`

Disabling katakana conversion can be done by setting `percentChanceToConvertToKatakana` to 0, and disabling font randomization can be done by setting `fontsToRandomlyChoose` to `[]`

# Licence
This addon is shares the same licence as Anki (GNU Affero General Public License 3).
