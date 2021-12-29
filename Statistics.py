
from Colors import Colors


class Statistics:
    CHAR_VAL_OF_ZERO = ord('0')
    CHAR_VAL_OF_NINE = ord('9')
    SOME_FUN_STATS = Colors.colored_string(Colors.colored_string("\n\nSome fun statistics:\n", Colors.UNDERLINE), Colors.OKGREEN)
    GAME_END_WINNER_MESSAGE = Colors.colored_string("The most pressed legal keys so far are:\n", Colors.OKGREEN)+"{keys} \n\n"
    GAME_MATCHES_SO_FAR = Colors.colored_string("The pairs matches so far\n",Colors.OKGREEN)
    VS = "{name0} VS {name1} - number of games so far: {number} \n"
    HALL_OF_FAME = Colors.colored_string("\n!!! QUICK MATHS HALL OF FAME !!!\n"  ,Colors.OKGREEN)
    FIRST_PLACE = Colors.colored_string("First place: ",Colors.OKGREEN) +"{name1}, "+Colors.colored_string("number of wins: ",Colors.OKGREEN)+"{score1}\n"
    SECOND_PLACE = Colors.colored_string("Second place: ",Colors.OKGREEN) +"{name1}, "+Colors.colored_string("number of wins: ",Colors.OKGREEN)+"{score1}\n"
    THIRD_PLACE = Colors.colored_string("Third place: ",Colors.OKGREEN) +"{name1}, "+Colors.colored_string("number of wins: ",Colors.OKGREEN)+"{score1}\n"
    THERE_ARENT_WINNERS =  Colors.colored_string("There aren't any winners yet, but you can fix that! \n", Colors.OKGREEN)

    def __init__(self):
        self.pressed_key = 10 * [0]
        self.teamsPairs = {}
        self.groups_wins = {}

    def add_key(self, key):
        if key!=None:
            if len(key)!=1:
                return None
            key_val = ord(key)
            if key_val >= self.CHAR_VAL_OF_ZERO & key_val <= self.CHAR_VAL_OF_NINE:
                self.pressed_key[key_val - self.CHAR_VAL_OF_ZERO] = self.pressed_key[key_val - self.CHAR_VAL_OF_ZERO] + 1

    def get_most_pressed(self):
        most = max(self.pressed_key)
        max_array = []
        for i in range(10):
            if self.pressed_key[i] == most:
                max_array.append(i)
        keys_string = ""
        for i in range(len(max_array)-1):
            keys_string=keys_string+chr(max_array[i]+self.CHAR_VAL_OF_ZERO)+", "
        keys_string = keys_string+chr(max_array[len(max_array)-1]+self.CHAR_VAL_OF_ZERO)
        return self.GAME_END_WINNER_MESSAGE.format(**{"keys": keys_string})

    def add_pair(self, name1, name2):
        if (name1, name2) in self.teamsPairs.keys():
            self.teamsPairs[(name1, name2)] = self.teamsPairs.get((name1, name2)) + 1
            return None
        if (name2, name1) in self.teamsPairs.keys():
            self.teamsPairs[(name2, name1)] = self.teamsPairs.get((name2, name1)) + 1
            return None
        self.teamsPairs[(name1, name2)] = 1

    def get_pairs_matches(self):
        str = self.GAME_MATCHES_SO_FAR
        for (name1, name2) in self.teamsPairs.keys():
            str = str + self.VS.format(**{"name0": name1,"name1": name2, "number":self.teamsPairs[(name1, name2)]})
        return str

    def add_group_win(self, group_name):
        if group_name in self.groups_wins.keys():
            self.groups_wins[group_name] = self.groups_wins.get(group_name)+1
        else:
            self.groups_wins[group_name] = 1

    def get_key(self, val, groups):
        for key, value in groups.items():
            if val == value:
                return key

        return "key doesn't exist"
    def get_group_win(self):
        str = self.HALL_OF_FAME
        if len(self.groups_wins)>=1:
            first_score = max(self.groups_wins.values())
            first_name = self.get_key(first_score, self.groups_wins)
            str = str + self.FIRST_PLACE.format(**{"name1": first_name,"score1": first_score})
            if len(self.groups_wins)>= 2:
                self.groups_wins.pop(first_name, first_score)
                second_score = max(self.groups_wins.values())
                second_name = self.get_key(second_score,self.groups_wins)
                str = str + self.SECOND_PLACE.format(**{"name1": second_name, "score1": second_score})
                if len(self.groups_wins) >= 2:
                    self.groups_wins.pop(second_name, second_score)
                    third_score = max(self.groups_wins.values())
                    third_name = self.get_key(third_score,self.groups_wins)
                    str = str + self.THIRD_PLACE.format(**{"name1": third_name, "score1": third_score})
                    self.groups_wins[second_name] = second_score
                self.groups_wins[first_name] = first_score
        else:
            str = str + self.THERE_ARENT_WINNERS
        return str

    def get_statistics(self):
        return self.SOME_FUN_STATS+self.get_most_pressed()+self.get_pairs_matches()+self.get_group_win()

