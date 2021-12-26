import random

class RandomQuestionGenerator:
    NUMBERS = [0, 1, 2 ,3, 4, 5, 6, 7, 8, 9]
    MAX_NUM = 9
    QUESTION_PHRASE = "How much is {operation}?"

    def __init__(self):
        pass

    def generate_plus_question():
        num1 = random.choice(NUMBERS)
        num2 = random.choice(NUMBERS[:MAX_NUM - num1])
        return QUESTION_PHRASE.format(**{"operation": num1 + " + " + num2})

    def generate_minus_question():
        num1 = random.choice(NUMBERS)
        num2 = random.choice(NUMBERS[:num1])
        return QUESTION_PHRASE.format(**{"operation": num1 + " - " + num2})

    def generate_product_question():
        num1 = random.choice(NUMBERS)
        num2 = random.choice(NUMBERS[:MAX_NUM / num1])
        return QUESTION_PHRASE.format(**{"operation": num1 + " * " + num2})

    def generate_random_math_question():
        generator = random.choice([generate_plus_question, generate_minus_question ,generate_product_question])
        return generator()