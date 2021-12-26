import random

class RandomQuestionGenerator():
    NUMBERS = [0, 1, 2 ,3, 4, 5, 6, 7, 8, 9]
    MAX_NUM = 9
    QUESTION_PHRASE = "How much is {operation}?"

    def __init__(self):
        pass

    def generate_plus_question(self):
        num1 = random.choice(self.NUMBERS)
        num2 = random.choice(self.NUMBERS[:self.MAX_NUM - num1])
        return self.QUESTION_PHRASE.format(**{"operation": num1 + " + " + num2})

    def generate_minus_question(self):
        num1 = random.choice(self.NUMBERS)
        num2 = random.choice(self.NUMBERS[:num1])
        return self.QUESTION_PHRASE.format(**{"operation": num1 + " - " + num2})

    def generate_product_question(self):
        num1 = random.choice(self.NUMBERS)
        num2 = random.choice(self.NUMBERS[:self.MAX_NUM / num1])
        return self.QUESTION_PHRASE.format(**{"operation": num1 + " * " + num2})

    def generate_random_math_question(self):
        generator = random.choice([self.generate_plus_question, self.generate_minus_question ,self.generate_product_question])
        return generator()