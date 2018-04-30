# To clean html
import justext
from bs4 import BeautifulSoup
# from boilerpipe.extract import Extractor # Boilerpipe is not currently being mantained. Removed till it comes back to live.


def preprocess_html(text, preprocessor, forcePeriod):
    """
        Options:
        preprocessor: justext, bs4, None
        continuous: True, False.

        Use continuous to set if you want to force end of sentences.
    """

    if not preprocessor or not (type(text) == str or type(text) == unicode) or len(text.strip()) == 0:
        print("TEXT IS NOT BEING PRE PROCESSED")
        print("type(text) == %s ; Size Text: %d" % (type(text), len(text.strip())))
        return text

    elif preprocessor == "bs4":
        soup = BeautifulSoup(text, "html.parser")
        tags_to_remove = ["script"]
        for tag in tags_to_remove:
            for x in soup.body(tag):
                x.decompose()
        if forcePeriod:
            return soup.body.get_text().replace("\n", ".\n")
        else:
            return soup.body.get_text()

    elif preprocessor == "justext":
        paragraphs = justext.justext(text, justext.get_stoplist('English'))
        text = "\n"
        for paragraph in paragraphs:
            if not paragraph.is_boilerplate: # and not paragraph.is_header:
                if forcePeriod:
                    text = text + paragraph.text + ".\n"
                else:
                    text = text + paragraph.text + "\n"
        return text

    # At the moment that this code was updated, boilerpipe was not available for download via pip.
    elif preprocessor == "boilerpipe" or preprocessor == "boi":
        text = Extractor(extractor='ArticleExtractor', html=text).getText()
        #print("Text before: %s" % text)
        if forcePeriod:
            #print("Text after: %s" % text.replace("\n", ".\n"))
            return text.replace("\n", ".\n")
        else:
            return text

    else:
        print("PRE PROCESSING OPTION %s NOT FOUND. IGNORING PRE PROCESSING." % (preprocessor))
        return text


