from aqt import mw, qt
from anki.hooks import addHook
from aqt.utils import showText
import shutil
import os
import random

class JapaneseRandomizer():
    def __init__(self):
        addHook('prepareQA', self.injectContent)
        self.addonPath = os.path.dirname(os.path.realpath(__file__))

        try:
            from aqt.gui_hooks import main_window_did_init
            main_window_did_init.append(self.onWindowInit)
        except:
            showText("Anki 2.1.28+ is required to use the Japanese Card Randomizer addon.")
            raise

    def onWindowInit(self):
        mediaDir = mw.col.media.dir()
        # Install the included fonts to the media folder if they don't already exist
        try:
            self.copyFont(mediaDir, self.addonPath + "/included_fonts/_hgrkk.ttf")
            self.copyFont(mediaDir, self.addonPath + "/included_fonts/_yugothb.ttc")
        except:
            pass
        
    def copyFont(self, mediaDir, fontFilePath):
        path = os.path.join(mediaDir, fontFilePath)
        if not os.path.exists(path):
            shutil.copy(fontFilePath, path)

    def injectContent(self, html, card, context):
        if context != 'reviewQuestion':
            return html
        config = mw.addonManager.getConfig(__name__)

        # Choose a font to change to (including not changing the font) randomly
        fontsToRandomlyChoose = config['fontsToRandomlyChoose'] or []
        fontIncludes = ""
        fontNames = []
        for fontUrl in fontsToRandomlyChoose:
            fontName = fontUrl.split(".")[0] # remove extension
            fontNames.append(fontName)
            fontIncludes += f"@font-face {{ font-family: {fontName}; src: url('{fontUrl}'); }}"

        randomIndex = random.randint(0,len(fontNames))-1 # This purposefully includes 0 to length so that we can subtract 1 to give us a choice of doing nothing
        changeFontFamilyLine = ""
        if randomIndex >= 0:
            changeFontFamilyLine = f"body {{ font-family:{fontNames[randomIndex]} !important; }}"

        injectedCode = f"<style>{fontIncludes} {changeFontFamilyLine}</style>"

        # Randomly change the entire page to swap katakana/hiragana
        percentChanceToConvertToKatakana = config['percentChanceToConvertToKatakana'] or 0.5
        convertToKatakana = random.uniform(0, 1) < percentChanceToConvertToKatakana
        if convertToKatakana:
            injectedCode += """
<script>
let hiragana = "ぁあぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをんゔゕゖ"
let katakana = "ァアィイゥウェエォオカガキギクグケゲコゴサザシジスズセゼソゾタダチヂッツヅテデトドナニヌネノハバパヒビピフブプヘベペホボポマミムメモャヤュユョヨラリルレロヮワヰヱヲンヴヵヶ"
let elements = document.getElementsByTagName('*');
for (let elementIndex = 0; elementIndex < elements.length; elementIndex++) {
    let element = elements[elementIndex];
    for (let childIndex = 0; childIndex < element.childNodes.length; childIndex++) {
        let node = element.childNodes[childIndex];
        if (node.nodeType === 3) {
            let text = node.nodeValue;
            let split = text.split('');
            for(let charIndex = 0; charIndex < split.length; charIndex++) {
                let hiraganaIndex = hiragana.indexOf(split[charIndex]);
                let katakanaIndex = katakana.indexOf(split[charIndex]);
                if(hiraganaIndex != -1) {
                    split[charIndex] = katakana[hiraganaIndex];
                }
                else if (katakanaIndex != -1)
                {
                    split[charIndex] = hiragana[katakanaIndex];
                }
            }
            let replacedText = split.join('');
            if (replacedText !== text) {
                let newNode = document.createTextNode(replacedText);
                element.replaceChild(newNode, node);
            }
        }
    }
}
</script>
"""
        return injectedCode + html
JapaneseRandomizer()