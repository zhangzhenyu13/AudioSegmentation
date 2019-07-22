import requests
import time
import random
import string
import json
import unicodedata
import  regex as re

def _is_whitespace(char):
    """Checks whether `chars` is a whitespace character."""
    # \t, \n, and \r are technically contorl characters but we treat them
    # as whitespace since they are generally considered as such.
    if char == " " or char == "\t" or char == "\n" or char == "\r":
        return True
    cat = unicodedata.category(char)
    if cat == "Zs":
        return True
    return False

def _is_control(char):
    """Checks whether `chars` is a control character."""
    # These are technically control characters but we count them as whitespace
    # characters.
    if char == "\t" or char == "\n" or char == "\r":
        return False
    cat = unicodedata.category(char)
    if cat.startswith("C"):
        return True
    return False

def _is_punctuation(char):
    """Checks whether `chars` is a punctuation character."""
    cp = ord(char)
    # We treat all non-letter/number ASCII as punctuation.
    # Characters such as "^", "$", and "`" are not in the Unicode
    # Punctuation class but we treat them as punctuation anyways, for
    # consistency.
    if ((cp >= 33 and cp <= 47) or (cp >= 58 and cp <= 64) or
            (cp >= 91 and cp <= 96) or (cp >= 123 and cp <= 126)):
        return True

    cat = unicodedata.category(char)
    if cat.startswith("P"):
        return True
    return False

def whitespace_tokenize(text):
    """Runs basic whitespace cleaning and splitting on a piece of text."""
    text = text.strip()
    if not text:
        return []
    tokens = text.split()
    return tokens

class BasicTokenizer(object):

    def tokenize(self, text):
        """Tokenizes a piece of text."""
        text = self._clean_text(text)
        orig_tokens = whitespace_tokenize(text)
        split_tokens = []
        for token in orig_tokens:
            split_tokens.extend(self._run_split_on_punc(token))
        output_tokens = whitespace_tokenize(" ".join(split_tokens))
        return output_tokens

    def _run_strip_accents(self, text):
        """Strips accents from a piece of text."""
        text = unicodedata.normalize("NFD", text)
        output = []
        for char in text:
            cat = unicodedata.category(char)
            if cat == "Mn":
                continue
            output.append(char)
        return "".join(output)

    def _run_split_on_punc(self, text):
        """Splits punctuation on a piece of text."""
        chars = list(text)
        i = 0
        start_new_word = True
        output = []
        while i < len(chars):
            char = chars[i]
            if _is_punctuation(char):
                output.append([char])
                start_new_word = True
            else:
                if start_new_word:
                    output.append([])
                start_new_word = False
                output[-1].append(char)
            i += 1
        return ["".join(x) for x in output]

    def _clean_text(self, text):
        """Performs invalid character removal and whitespace cleanup on text."""
        output = []
        for char in text:
            cp = ord(char)
            if cp == 0 or cp == 0xfffd or _is_control(char):
                continue
            if _is_whitespace(char):
                output.append(" ")
            else:
                output.append(char)
        return "".join(output)

class TextNormalizer(object):
    __retry_service=5
    __TN_type={1:"None", 2:"WfstInverseTextNormalization", 3:"ImplicitPunctuation", 4:"ImplicitPunctuation"}
    __tokenizer=BasicTokenizer()

    @staticmethod
    def itn_response(hyp):
        '''
        network restAPI service
        :param hyp: input raw transcript
        :return: normalized text
        '''
        rawhyp = hyp
        url = "http://speech.platform.bing-int.com/internal/dpp/speech/processtext/officedictate/nbest/v1"
        payload = "{\r\n\t\"Features\": [{\r\n\t\t\"type\": \"InverseTextNormalization\"\r\n\t}, {\r\n\t\t\"type\": \"Capitalization\"\r\n\t}, {\r\n\t\t\"type\": \"Reformulation\"\r\n\t}, {\r\n\t\t\"type\": \"ImplicitPunctuation\"\r\n\t}, {\r\n\t\t\"type\": \"ExplicitPunctuation\"\r\n\t}, {\r\n\t\t\"type\": \"ProfanityMasking\"\r\n\t}],\r\n\t\"Context\": {\r\n\t\t\"locale\": \"en-us\",\r\n\t\t\"nBest\": [{\r\n\t\t\t\"Text\": \"" + rawhyp + "\"\r\n\t\t}],\r\n\t\t\"positionContext\": {\r\n\t\t\t\"left\": \"\",\r\n\t\t\t\"right\": \"\"\r\n\t\t}\r\n\t}\r\n}"
        headers = {
            'Content-Type': "application/json",
            'Accept': "*/*",
            'Cache-Control': "no-cache",
            'Host': "speech.platform.bing-int.com",
            'accept-encoding': "gzip, deflate",
            'content-length': "401",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        }
        response = requests.request("POST", url, data=payload, headers=headers)
        return response

    @staticmethod
    def itn(hyp):
        succeeded = False
        num_retries = 0
        while not succeeded and num_retries<TextNormalizer.__retry_service:
            try:
                num_retries+=1
                response = TextNormalizer.itn_response(hyp)
                if response.status_code!=200:
                    print("response status error:", response)
                    time.sleep(random.randint(5, 15))
                    continue

                #print(response)
                #print(response.text)
                response=json.loads(response.text)
                #print("stages",response["stages"])
                TN=response["stages"][-1]["nBest"][0]["text"]
                return {"success":True, "TN":TN}
            except:
                return {"success":False, "TN":""}

    @staticmethod
    def remove_punct(text):
        return " ".join(
            filter( lambda c: len(c)>1 or not _is_punctuation(c), TextNormalizer.__tokenizer.tokenize(text) )
        )

    @staticmethod
    def remove_vivid(text):
        return re.sub(r"\[(.*?)\]", "", text)

    @staticmethod
    def remove_person(text):
        words=text.split()
        n=4
        ngrams = [(s, e + 1)
                  for s in range(len(words))
                  for e in range(s, min(s + n, len(words)))
                  if not words[s:e + 1][-1]==':' ]


        return re.sub(r"\s+.*?:\s+", " ", text)
        pass

    @staticmethod
    def normalize_vtt(transcript):
        transcript = transcript.replace('\n', ' ')
        transcript = transcript.replace(u'\u2013', '-')
        transcript = transcript.replace(u'\u2018', '"')
        transcript = transcript.replace(u'\u2019', '"')
        transcript = transcript.replace(u'\u201c', '\'')
        transcript = transcript.replace(u'\u201d', '\'')
        transcript = transcript.replace(u'\u2026', '...')
        transcript = transcript.replace(u'"', '\'')
        transcript = TextNormalizer.itn(transcript)



        return transcript

    @staticmethod
    def endSent(line):
        if line:
            if line[-1] in ('?','.', '!'):
                return True
        return False