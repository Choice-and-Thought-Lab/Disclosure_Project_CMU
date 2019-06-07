from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants
import re
import time
import random


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
            self.player.set_timeout_data()


# show EXAMPLE image based on role
class Intro2(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


# class AdvComm3(Page):
class AdvPaymentScheme(Page):
    form_model = 'player'
    form_fields = ['manip_adv_adviser_payment_question',
                   'manip_adv_estimator_payment_question']

    def manip_adv_adviser_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def manip_adv_estimator_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_adviser() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


# class AdvComm4(Page):
class DisclosureInfo(Page):
    form_model = 'player'

    def get_form_fields(self):
        print('isadviser', self.player.is_adviser())
        if self.player.is_adviser():
            if self.player.disclosure:
                return ['manip_adv_payment_scheme_disclosed']
            else:
                return ['manip_adv_payment_scheme_not_disclosed']
        else:
            return []

    def manip_adv_payment_scheme_disclosed_error_message(self, value):
        if value == False and self.player.is_adviser():
            return 'Not the right choice. Please read the instructions carefully'

    def manip_adv_payment_scheme_not_disclosed_error_message(self, value):
        if value == False and self.player.is_adviser():
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_adviser() or self.player.is_estimator()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class AdvBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_adviser() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


# class AdvComm7(Page):
class AdvAdvice(Page):
    # this to keep the value entered by each adviser only to that player
    form_model = 'player'
    form_fields = ['recommendation']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_adviser()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class WaitForRecommendation(WaitPage):
    template_name = 'study/WaitProgress.html'

    def is_displayed(self):
        return False  # self.player.is_adviser() #or self.player.is_estimator()

    def vars_for_template(self):
        return {
            'adviser': self.group.get_player_by_role('adviser').participant,
            'estimator': self.group.get_player_by_role('estimator').participant,
            'judge': self.group.get_player_by_role('judge').participant
        }


# class EstComm2(Page):
class EstPaymentScheme(Page):
    form_model = 'player'
    form_fields = ['manip_est_estimator_payment_question']

    def manip_est_estimator_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class EstBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        self.player.prep_before_decision()
        if self.timeout_happened:
            self.player.set_timeout_data()


class EstEstimate(Page):
    form_model = 'player'
    form_fields = ['estimate']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator()

    def before_next_page(self):
        self.player.calculate_grid_rewards()
        if self.timeout_happened:
            self.player.set_timeout_data()


class EstRevealPreamble(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class WaitForEstimate(WaitPage):
    template_name = 'study/WaitProgress.html'

    def vars_for_template(self):
        return {
            'adviser': self.group.get_player_by_role('adviser').participant,
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
            self.player.set_timeout_data()


class EstReveal(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def vars_for_template(self):
        return {'adviser_reward': self.group.get_player_by_role('adviser').grid_reward}

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class EstAppeal(Page):
    form_model = 'player'
    form_fields = ['appealed']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class EstPostAppeal(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class JudgeBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge()

    def before_next_page(self):
        self.player.prep_before_decision()
        if self.timeout_happened:
            self.player.set_timeout_data()

class JudgeEstimatorInfo(Page):
    form_model = 'player'
    form_fields = ['manip_est_judge_payment_question']

    def manip_est_judge_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()

class JudgeAdvisorInfo(Page):
    form_model = 'player'
    form_fields = ['manip_adv_judge_payment_question']

    def manip_adv_judge_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()

class JudgeExample(Page):
    form_model = 'player'

    def manip_adv_judge_payment_question_error_message(self, value):
        if value == False:
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()



class JudgeCaseAndJudgment(Page):
    form_model = 'player'
    form_fields = ['appeal_granted']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge()

    def before_next_page(self):
        if self.player.appeal_granted:
            self.player.recalculate_payOffs_with_appeal(True)
        else:
            self.player.recalculate_payOffs_with_appeal(False)

        if self.timeout_happened:
            self.player.set_timeout_data()


class WaitForJudgment(WaitPage):
    template_name = 'study/WaitProgress.html'

    def vars_for_template(self):
        return {
            'adviser': self.group.get_player_by_role('adviser').participant,
            'estimator': self.group.get_player_by_role('estimator').participant,
            'judge': self.group.get_player_by_role('judge').participant
        }


class Blame(Page):
    form_model = 'player'

    def get_form_fields(self):
        if self.player.is_estimator():
            return ['blame_EST_I_blame_myself_for_my_guess',
                    'blame_EST_I_blame_the_adviser_for_my_guess',
                    'blame_EST_I_have_a_legitimate_grievance_against_the_adviser',
                    'blame_EST_I_have_a_strong_case_if_I_choose_to_pursue_an_appeal',
                    'blame_EST_I_believe_that_others_would_rule_in_my_favor',
                    'blame_EST_The_adviser_treated_me_fairly',
                    'blame_EST_I_was_mistreated_by_the_adviser',
                    'blame_EST_I_deserve_to_receive_the_full_bonus'
                    ]
        elif self.player.is_judge():
            return ['blame_JUDGE_I_blame_the_estimator_for_their_guess',
                    'blame_JUDGE_I_blame_the_adviser_for_the_estimators_guess',
                    'blame_JUDGE_estimator_has_legitimate_grievance_against_adviser',
                    'blame_JUDGE_estimator_has_a_strong_case_to_pursue_an_appeal',
                    'blame_JUDGE_I_believe_others_would_rule_in_estimators_favor',
                    'blame_JUDGE_The_adviser_treated_the_estimator_fairly',
                    'blame_JUDGE_The_estimator_was_mistreated_by_the_adviser',
                    'blame_JUDGE_The_estimator_deserves_to_receive_the_full_bonus']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return (not self.player.is_adviser()) and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class PostQuestions(Page):
    # Manipulation Checks
    form_model = 'player'
    form_fields = ['manip_final_adviser_payment_question',
                   'manip_final_estimator_payment_question', 'manip_final_conflict_disclosed_or_not']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()

    def vars_for_template(self):
        return {'header': "To verify that you understood the dot-estimation task, please answer the following three questions:"}

class ClarificationQuestions(Page): 
    form_model = 'player'
    form_fields = ['estimator_appeal_question', 'judge_bonus_awarded_clarify', 'judge_bonus_not_awarded_clarify']
    
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()

    def is_displayed(self):
        return (not self.player.is_adviser()) and self.participant.vars['expiry'] - time.time() > 3

    def vars_for_template(self):
        return {'header': "To help us understand why you made the decision you did ,please answer the following question"}


class Conclusion(Page):
    def vars_for_template(self):
        return {
            'appeal_reward_minus_cost': Constants.appeal_reward - Constants.appeal_cost,
            'appeal_reward_split_minus_cost': Constants.appeal_reward_split - Constants.appeal_cost,
            'estimator_grid_reward': self.group.get_player_by_role('estimator').grid_reward,
            'adviser_grid_reward': self.group.get_player_by_role('adviser').grid_reward
        }

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class Demographics1(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class Demographics2(Page):
    form_model = 'player'
    form_fields = ['d1', 'd2', 'd3', 'd4', 'd5']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class Comments(Page):
    form_model = 'player'
    form_fields = ['comment']

    def is_displayed(self):
        return self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


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
    DisclosureInfo,
    AdvBegin,
    EstBegin,
    AdvAdvice,
    EstEstimate,
    EstRevealPreamble,
    EstReveal,
    EstAppeal,
    EstPostAppeal,
    JudgeEstimatorInfo,
    JudgeAdvisorInfo,
    JudgeExample,
    JudgeBegin,
    JudgeCaseAndJudgment,
    Blame,
    PostQuestions,
    ClarificationQuestions,
    Demographics1,
    Demographics2,
    Comments,
    Finish
]
