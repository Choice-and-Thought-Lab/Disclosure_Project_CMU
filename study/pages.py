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
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


# class AdvComm4(Page):
class DisclosureInfo(Page):
    form_model = 'player'

    def get_form_fields(self):
        print('isadvisor', self.player.is_advisor())
        if self.player.is_advisor():
            if self.player.disclosure:
                return ['manip_adv_payment_scheme_disclosed']
            else:
                return ['manip_adv_payment_scheme_not_disclosed']
        else:
            return []

    def manip_adv_payment_scheme_disclosed_error_message(self, value):
        if value == False and self.player.is_advisor():
            return 'Not the right choice. Please read the instructions carefully'

    def manip_adv_payment_scheme_not_disclosed_error_message(self, value):
        if value == False and self.player.is_advisor():
            return 'Not the right choice. Please read the instructions carefully'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() or self.player.is_estimator()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


class AdvBegin(Page):
    template_name = 'study/Begin.html'

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor() and self.participant.vars['expiry'] - time.time() > 3

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


# class AdvComm7(Page):
class AdvAdvice(Page):
    # this to keep the value entered by each advisor only to that player
    form_model = 'player'
    form_fields = ['recommendation']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_advisor()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()


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
            self.player.set_timeout_data()


class EstReveal(Page):
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_estimator() and self.participant.vars['expiry'] - time.time() > 3

    def vars_for_template(self):
        return {'advisor_reward': self.group.get_player_by_role('advisor').grid_reward}

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
    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def is_displayed(self):
        return self.player.is_judge()

    def before_next_page(self):
        self.player.prep_before_decision()
        if self.timeout_happened:
            self.player.set_timeout_data()


class JudgeCaseAndJudgement(Page):
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
            self.player.set_timeout_data()

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

    def get_form_fields(self):
        if self.player.disclosure:
            return ['manip_final_adviser_payment_question', 'manip_final_estimator_payment_question', 'manip_final_payment_scheme_disclosed']
        else:
            return ['manip_final_adviser_payment_question', 'manip_final_estimator_payment_question', 'manip_final_payment_scheme_not_disclosed']

    def get_timeout_seconds(self):
        return self.participant.vars['expiry'] - time.time()

    def before_next_page(self):
        if self.timeout_happened:
            self.player.set_timeout_data()

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
    JudgeBegin,
    JudgeCaseAndJudgement,
    ManipulationChecks,
    Demographics1,
    Demographics2,
    Comments,
    Finish
]
