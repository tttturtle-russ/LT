from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline

model_dict = {
    'nllb-1.3B': 'facebook/nllb-200-1.3B',
    'nllb-3.3B': 'facebook/nllb-200-3.3B',
    'nllb-distilled-600M': 'facebook/nllb-200-distilled-600M',
    'nllb-distilled-1.3B': 'facebook/nllb-200-distilled-1.3B',
}


class Translator:
    def __init__(self, model_id, repo):
        self.model_id = model_id
        self.repo = repo
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_dict[self.model_id])
        self.tokenizer = AutoTokenizer.from_pretrained(model_dict[self.model_id])
        self.translator = pipeline(
            'translation',
            model=self.model,
            tokenizer=self.tokenizer,
            src_lang="eng_Latn",
            dst_lang="zho_Hans"
        )

    def translate(self, original):
        return self.translator(original)[0]['translation_text']



