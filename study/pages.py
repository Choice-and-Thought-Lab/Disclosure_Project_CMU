from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import re
import time
import random


# These pages roughly follow the page divisions as specified in the Qualtrics survey.

class Consent(Page):
    form_model = 'player'
    form_fields = ['consent18', 'consentRead', 'consentWant', 'mTurkId']

    def before_next_page(self):
        # user has 60 minutes to complete as many pages as possible
        self.participant.vars['expiry'] = time.time() + 3600
        # self.player.disclosure = random.choice([True, False])

    def error_message(self, values):
        if values["consent18"] != True or values["consentRead"] != True or values["consentWant"] != True:
            return 'Sorry, but you are not eligible for this study.'
        if values["mTurkId"] == '':
            return 'Please enter a valid mTurkId.'


# "You will play the role of %role%."
class Intro1(Page):
    form_model = 'player'
    form_fields = ['mTurkId']

    def error_message(self, values):
        if len(values["mTurkId"]) < 5:
            return 'Please enter a valid mTurkId.'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        self.participant.vars['expiry'] = time.time() + 100000
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


# show EXAMPLE image based on role
class Intro2(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


# AdvComm: Communication pages for the advisor
class AdvComm1(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class AdvComm2(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


# class AdvComm3(Page):
class AdvPaymentScheme(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class AdvComm4(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class AdvBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class AdvComm5(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class AdvComm6(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


# class AdvComm7(Page):
class CommunicationFormAdvEst(Page):
    # this to keep the value entered by each advisor only to that player
    form_model = 'player'
    form_fields = ['recommendation']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class WaitForRecommendation(WaitPage):
    template_name = 'study/WaitProgress.html'

    def is_displayed(self):
        return False  # self.player.is_advisor() #or self.player.is_estimator()

    def vars_for_template(self):
        return {
            'advisor': self.group.get_player_by_role('advisor').participant,
            'estimator': self.group.get_player_by_role('estimator').participant,
            'judge': self.group.get_player_by_role('judge').participant
        }


class EstComm1(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


# class EstComm2(Page):
class EstPaymentScheme(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstComm3(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstComm4(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstComm5(Page):
    # form_model = 'group'(Chaged from group to players)
    form_model = 'player'
    # form_model = 'group'
    form_fields = ['estimate']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        # self.player.calculate_grid_rewards()  # this function is only executed once: once the estimator advances.
        # this function is only executed once: once the estimator advances.
        self.group.calculate_grid_rewards()
        if self.timeout_happened:
            self.player.set_model_data()


class EstComm6(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class WaitForEstimate(WaitPage):
    template_name = 'study/WaitProgress.html'

    def vars_for_template(self):
        return {
            'advisor': self.group.get_player_by_role('advisor').participant,
            'estimator': self.group.get_player_by_role('estimator').participant,
            'judge': self.group.get_player_by_role('judge').participant
        }


class RevealGrid(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class GridReward(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        # Removed for advisor
        # return self.player.is_advisor() or self.player.is_estimator()
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstInfo1(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()

    def vars_for_template(self):
        return {
            # 'row2_lower': self.player.get_correct_answer() - 10,
            # 'row2_upper': self.player.get_correct_answer(),
            # 'row3_lower': self.player.get_correct_answer() + 1,
            # 'row3_upper': self.player.get_correct_answer() + 10,
            # 'row4_lower': self.player.get_correct_answer() + 11,
            # 'row4_upper': self.player.get_correct_answer() + 99,
            'correct_answer_minus10': self.player.get_correct_answer() - 10,
            'correct_answer_minus20': self.player.get_correct_answer() - 20,
            'correct_answer_minus30': self.player.get_correct_answer() - 30,
            'correct_answer_minus40': self.player.get_correct_answer() - 40,
            'correct_answer_plus10': self.player.get_correct_answer() + 10,
            'correct_answer_plus20': self.player.get_correct_answer() + 20,
            'correct_answer_plus30': self.player.get_correct_answer() + 30,
            'correct_answer_plus40': self.player.get_correct_answer() + 40,
        }


class EstInfo2(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def vars_for_template(self):
        return {'advisor_reward': self.group.get_player_by_role('advisor').grid_reward}

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstAppeal1(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstAppeal2(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstAppeal3(Page):
    form_model = 'group'
    form_fields = ['appealed']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class EstAppeal4(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class JudgeInfo1(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class JudgeInfo2(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class JudgeInfo3(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()

    def vars_for_template(self):
        return {
            # 'row2_lower': self.player.get_correct_answer() - 10,
            # 'row2_upper': self.player.get_correct_answer(),
            # 'row3_lower': self.player.get_correct_answer() + 1,
            # 'row3_upper': self.player.get_correct_answer() + 10,
            # 'row4_lower': self.player.get_correct_answer() + 11,
            # 'row4_upper': self.player.get_correct_answer() + 99,
            'correct_answer_minus10': self.player.get_correct_answer() - 10,
            'correct_answer_minus20': self.player.get_correct_answer() - 20,
            'correct_answer_minus30': self.player.get_correct_answer() - 30,
            'correct_answer_minus40': self.player.get_correct_answer() - 40,
            'correct_answer_plus10': self.player.get_correct_answer() + 10,
            'correct_answer_plus20': self.player.get_correct_answer() + 20,
            'correct_answer_plus30': self.player.get_correct_answer() + 30,
            'correct_answer_plus40': self.player.get_correct_answer() + 40,

            'advisor_reward': self.group.get_player_by_role('advisor').grid_reward,
            'estimator_reward': self.group.get_player_by_role('estimator').grid_reward
        }


class JudgeInfo4(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class JudgeInfo5(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()

    def vars_for_template(self):
        return {
            'advisor_upper_bound': self.player.get_correct_answer() + 40,
            'estimator_lower_bound': self.player.get_correct_answer() - 10,
            'estimator_upper_bound': self.player.get_correct_answer() + 10,
            'correct_answer_minus10': self.player.get_correct_answer() - 10,
            'correct_answer_minus20': self.player.get_correct_answer() - 20,
            'correct_answer_minus30': self.player.get_correct_answer() - 30,
            'correct_answer_minus40': self.player.get_correct_answer() - 40,
            'correct_answer_plus10': self.player.get_correct_answer() + 10,
            'correct_answer_plus20': self.player.get_correct_answer() + 20,
            'correct_answer_plus30': self.player.get_correct_answer() + 30,
            'correct_answer_plus40': self.player.get_correct_answer() + 40,
        }


class JudgeInfo6(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class JudgeInfo7(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()

    def vars_for_template(self):
        return {
            # 'row2_lower': self.player.get_correct_answer() - 10,
            # 'row2_upper': self.player.get_correct_answer(),
            # 'row3_lower': self.player.get_correct_answer() + 1,
            # 'row3_upper': self.player.get_correct_answer() + 10,
            # 'row4_lower': self.player.get_correct_answer() + 11,
            # 'row4_upper': self.player.get_correct_answer() + 99,
            'correct_answer_minus10': self.player.get_correct_answer() - 10,
            'correct_answer_minus20': self.player.get_correct_answer() - 20,
            'correct_answer_minus30': self.player.get_correct_answer() - 30,
            'correct_answer_minus40': self.player.get_correct_answer() - 40,
            'correct_answer_plus10': self.player.get_correct_answer() + 10,
            'correct_answer_plus20': self.player.get_correct_answer() + 20,
            'correct_answer_plus30': self.player.get_correct_answer() + 30,
            'correct_answer_plus40': self.player.get_correct_answer() + 40,

            'advisor_reward': self.group.get_player_by_role('advisor').grid_reward,
            'estimator_reward': self.group.get_player_by_role('estimator').grid_reward
        }


class Judgment(Page):
    form_model = 'group'
    form_fields = ['appeal_granted']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.group.appeal_granted:
            self.group.recalculate_payOffs_with_appeal(True)
        else:
            self.group.recalculate_payOffs_with_appeal(False)
        if self.timeout_happened:
            self.player.set_model_data()


class WaitForJudgment(WaitPage):
    template_name = 'study/WaitProgress.html'

    def vars_for_template(self):
        return {
            'advisor': self.group.get_player_by_role('advisor').participant,
            'estimator': self.group.get_player_by_role('estimator').participant,
            'judge': self.group.get_player_by_role('judge').participant
        }


class AdvPostJudgment(Page):

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()

    # Removed for Advisor
    # class Blame(Page):
    # template_name = "study/PostQuestions.html"

    form_model = 'group'

    def get_form_fields(self):
        if self.player.is_estimator():
            return ['e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8', 'e9']
        elif self.player.is_judge():
            return ['j1', 'j2', 'j3', 'j4', 'j5', 'j6', 'j7', 'j8', 'j9']
        elif self.player.is_advisor():
            return ['a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8', 'a9']

    def vars_for_template(self):
        return {'header': "Now we'd like to ask you to rate your level of agreement with a series of statements."}


class ManipulationChecks(Page):
    template_name = "study/PostQuestions.html"

    form_model = 'player'
    form_fields = ['m1', 'm2', 'm3']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    # Prior to conclusion, calculate total rewards
    def before_next_page(self):
        # self.player.assign_rewards() # Saran - commenting because we need to assign rewards at group level
        if self.timeout_happened:
            self.player.set_model_data()

    def vars_for_template(self):
        return {'header': "Please answer the following three questions about the survey."}


class Conclusion(Page):
    def vars_for_template(self):
        return {
            'appeal_reward_minus_cost': Constants.appeal_reward - Constants.appeal_cost,
            'appeal_reward_split_minus_cost': Constants.appeal_reward_split - Constants.appeal_cost,
            'estimator_grid_reward': self.group.get_player_by_role('estimator').grid_reward,
            'advisor_grid_reward': self.group.get_player_by_role('advisor').grid_reward
        }

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class Demographics1(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class Demographics2(Page):
    form_model = 'player'
    form_fields = ['d1', 'd2', 'd3', 'd4', 'd5']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class Comments(Page):
    form_model = 'player'
    form_fields = ['comment']

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_model_data()


class Finish(Page):
    form_model = 'player'
    form_fields = ['email', 'entered_email']

    def error_message(self, values):
        email_pattern = re.compile(
            r"(^$|(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$))")
        if (
                (values['entered_email'] is True and values['email'] is None) or
                (values['entered_email']
                 is True and not email_pattern.match(values['email']))
        ):
            return "Invalid email address"


page_sequence = [
    # Consent,
    Intro1,
    Intro2,
    AdvPaymentScheme,
    EstPaymentScheme,
    # AdvComm1,
    # AdvComm2,
    # AdvComm3,
    # AdvComm4,
    AdvBegin,
    # AdvComm5,
    # AdvComm6,
    # AdvComm7,
    # EstComm1,
    # EstComm2,
    EstBegin,
    EstComm3,
    EstComm4,
    EstComm5,
    EstComm6,
    GridReward,
    EstInfo2,
    EstAppeal1,
    EstAppeal2,
    EstAppeal3,
    EstAppeal4,
    JudgeInfo1,
    JudgeInfo3,
    JudgeInfo4,
    JudgeInfo5,
    JudgeInfo6,
    JudgeInfo7,
    Judgment,
    ManipulationChecks,
    Demographics1,
    Demographics2,
    Comments,
    Finish
]
