from aqt import mw, qt
from anki.hooks import addHook
from aqt.utils import showText, showWarning
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

    def isFeatureEnabled(self, configLine, deckName):
        return not (len(configLine) > 0 and (deckName not in configLine))

    def injectContent(self, html, card, context):
        if context != 'reviewQuestion':
            return html
        config = mw.addonManager.getConfig(__name__)
        if config == None:
            showWarning("""There was an error loading the config for the Japanese Randomizer Add-on. 
Please check that the format is correct.
If the problem persists try redownloading the add-on. Otherwise create an issue on github describing the problem https://github.com/Toocanzs/AnkiJapaneseCardRandomizer/issues/new
""")
            return html
        
        deck = mw.col.decks.get(card.did)
        deckName = deck['name']
        if not self.isFeatureEnabled(config['globalDeckLimitation'], deckName):
            return html

        injectedCode = ""

        # Choose a font to change to (including not changing the font) randomly
        fontsToRandomlyChoose = config['fontRandomizer']['fontsToRandomlyChoose']
        fontIncludes = ""
        fontNames = []
        for fontUrl in fontsToRandomlyChoose:
            fontName = fontUrl.split(".")[0] # remove extension
            fontNames.append(fontName)
            fontIncludes += f"@font-face {{ font-family: {fontName}; src: url('{fontUrl}'); }}"

        randomIndex = random.randint(0,len(fontNames))-1 # This purposefully includes 0 to length so that we can subtract 1 to give us a choice of doing nothing if randomIndex = -1
        if not self.isFeatureEnabled(config['fontRandomizer']['limitedToTheseDecks'], deckName):
            randomIndex = 0

        changeFontFamilyLine = ""
        if randomIndex >= 0:
            changeFontFamilyLine = f"body {{ font-family:{fontNames[randomIndex]} !important; }}"
            injectedCode += f"<style>{fontIncludes} {changeFontFamilyLine}</style>"

        # Randomly change the entire page to swap katakana/hiragana
        percentChanceToConvertToKatakana = config['katakanaConverter']['chance']
        convertToKatakana = random.uniform(0, 1) < percentChanceToConvertToKatakana

        injectedCode += "<script>\n"

        percentChanceConvertVertical = config['verticalText']['chance']
        convertVertical = random.uniform(0, 1) < percentChanceConvertVertical
        if convertVertical and self.isFeatureEnabled(config['verticalText']['limitedToTheseDecks'], deckName):
            injectedCode += """let expressions = document.querySelectorAll(".expression-field, .migaku-word-front");
            
for(let expressionIndex = 0; expressionIndex < expressions.length; expressionIndex++)
{
    let expression = expressions[expressionIndex];
    expression.style.writingMode = "vertical-rl";
    traverseChildNodes(expression);
}

  function traverseChildNodes(node) {
      var next;
      if (node.nodeType === 1) {
          // (Element node)
          if (node = node.firstChild) {
              do {
                  // Recursively call traverseChildNodes
                  // on each child node
                  next = node.nextSibling;
                  traverseChildNodes(node);
              } while(node = next);
          }
      } else if (node.nodeType === 3) {
        convertAsciiUpright(node);
      }
  }

function convertAsciiUpright(node) {
    let text = node.nodeValue;
    let split = [];
    // Split by japanese support stuff (like readings and pitch accent)
    // Then split by ascii and throw everything into the split array.
    // This way we can check if something is a japanese support thing later and skip it, otherwise we'd convert the ascii letters inside the japanese support thing to upright which would break it
    const supportRegex = /( *\[[^\]]*])/g;
    const asciiRegex = /([0-9a-zA-Z?“!”]+)/g;
    
    text.split(supportRegex).forEach(x=>{
        if(x.match(supportRegex)) 
            split.push(x); // Just push as is, no spllitting otherwise we turn "[がくえん;h]" to "[がくえん;", "h", "]"
        else
            x.split(asciiRegex).forEach(y=>split.push(y))
    });
    
    // Convert ascii stuff to upright so it's easier to read
    split = split.map(x=>{
        console.log(x);
        if(x.match(supportRegex)) 
            return x;
        if(x.match(asciiRegex))
            return "<span style=\\"text-orientation: upright;\\">"+x+"</span>";
        return x;
    })
    
    // Replace text with our new nodes
    let newNode = document.createElement("span");
    newNode.innerHTML = split.join("");
    while (newNode.firstChild) {
        node.parentNode.insertBefore(newNode.firstChild, node);
    }
    node.parentNode.removeChild(node);
}
"""
        if convertToKatakana and self.isFeatureEnabled(config['katakanaConverter']['limitedToTheseDecks'], deckName):
            injectedCode += """
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
                node = newNode;
            }
        }
    }
}
"""
        injectedCode += "</script>"
        return injectedCode + html
JapaneseRandomizer()