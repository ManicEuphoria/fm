from collections import OrderedDict
# The rules of judgement part


def get_results(result_id):
    # final rule
    basic_emotion_range = lambda x: x.emotion.emotion_range
    extra_emo_range = lambda x: x.emotion.extra_emotion_range
    close_emo_range = lambda x: x.emotion.close_emotion_range
    basic_tag = lambda x: x.tag.last_tag

    final_rule = {
        '1': [basic_emotion_range, basic_tag, "lib", "level", None],
        "2": [basic_emotion_range, None, 'lib', "level", None],
        "3": [close_emo_range, basic_tag, "lib", 'order', None],
        '4': [extra_emo_range, basic_tag, 'lib', "order", None],
        '5': [extra_emo_range, None, "lib", 'order', None],
        "6": [extra_emo_range, basic_tag, 'rec', "order", None],
        '7': [extra_emo_range, None, "rec", "order", None],
        '8': [None, None, "rec", "order", 100],

    }
    return final_rule[result_id]


class Rule(object):
    def __init__(self):
        self.track_branch = lambda x: x.track_number.show()
        self.is_still_playing = lambda x: x.track_number.continue_playing
        self.last_tag_exist = lambda x: True if x.tag.last_tag else False
        self.has_source = lambda x: x.track_number.has_source

        self.rule1 = [("track_branch", 0), ('is_still_playing', True),
                      ("last_tag_exist", False), ("result", "1")]
        self.rule2 = [('track_branch', 0), ("is_still_playing", False),
                      ('result', "2")]
        self.rule3 = [('track_branch', 0), ("is_still_playing", True),
                      ("last_tag_exist", True), ('result', "3")]

        self.rule4 = [("track_branch", 1), ("last_tag_exist", True),
                      ("result", "4")]
        self.rule5 = [('track_branch', 1), ('last_tag_exist', False),
                      ("result", "5")]

        self.rule6 = [('track_branch', 2), ("has_source", False),
                      ('last_tag_exist', True), ("result", "6")]
        self.rule7 = [('track_branch', 2), ('has_source', False),
                      ('last_tag_exist', False), ("result", "7")]
        self.rule11 = [("track_branch", 2), ("has_source", True),
                       ('result', "8")]
        self.rule8 = [('track_branch', 3), ('last_tag_exist', True),
                      ("result", "4")]
        self.rule8 = [('track_branch', 3), ('last_tag_exist', False),
                      ("result", "5")]

        self.rule9 = [('track_branch', 4), ('has_source', False),
                      ('last_tag_exist', True), ("result", "6")]
        self.rule10 = [('track_branch', 4), ('has_source', False),
                       ('last_tag_exist', False), ("result", "7")]
        self.rule12 = [('track_branch', 4), ("has_source", True),
                       ("result", "8")]
        self.all_rules = []
        for i in range(1, 13):
            self.all_rules.append(getattr(self, "rule%s" % (i)))


def track_rule(rule_type, cache_status):
    # The rules of judgement part
    tr = Rule()
    index = 0
    valid_rules = tr.all_rules
    while 1:
        valid_rules = [
            rule for rule in valid_rules
            if getattr(tr, rule[index][0])(cache_status) == rule[index][1]]
        if len(valid_rules) == 1:
            result_id = valid_rules[0][-1][1]
            funcs = get_results(result_id)
            return funcs[0: 3] if rule_type == "filter" else funcs[3:]
        else:
            index += 1
