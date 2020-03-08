import os
import random
import re
import time
from django.contrib.staticfiles.templatetags.staticfiles import static
from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)

author = 'Aaron Yao-Smith'
modification_author = ['Saran Prasad Ambikapathy', 'Hung Nguyen']

doc = """
Incentive Compatible Disclosure Study
"""


def make_Likert_agreement(label):
    return models.IntegerField(
        choices=[
            [7, "Strongly agree"],
            [6, "Agree"],
            [5, "Somewhat agree"],
            [4, "Neither agree nor disagree"],
            [3, "Somewhat disagree"],
            [2, "Disagree"],
            [1, "Strongly disagree"]
        ],
        label=label,
        widget=widgets.RadioSelect
    )

def judge_bonus_label(appeal):
    if (appeal):
        return "the estimator should receive " + str(Constants.appeal_reward) + " and the adviser should receive nothing"
    else: 
        return "the estimator and adviser should both receive " + str(Constants.appeal_reward_split)

def judge_bonus_field(appeal):
    return models.LongStringField(
        label= "Why did you decide that " + judge_bonus_label(appeal) + "?",
        blank=True)

class Constants(BaseConstants):
    name_in_url = 'study'
    players_per_group = 6
    num_rounds = 1

    # base reward for completing the survey
    base_reward = c(0.5)  

    # New PayOffs - estimator
    # (-inf, -40)
    estimator_bonus_less_than_neg_40 = c(0)
    # [-40, -10)  
    estimator_bonus_within_neg_40_and_neg_10 = c(2)
    # [-10, 10]
    estimator_bonus_within_neg_10_and_10 = c(5)
    # (10, 40]
    estimator_bonus_within_10_and_40 = c(2)
    # (40, inf)
    estimator_bonus_greater_than_40 = c(0)

    # New PayOffs - adviser
    # (-inf, 10]
    adviser_bonus_less_than_10 = c(0)
    # (10, 40]
    adviser_bonus_within_10_and_40 = c(2)
    # (40, inf)
    adviser_bonus_greater_than_40 = c(5)
    
    appeal_reward = c(2)  # given to estimator on appeal win
    appeal_reward_split = appeal_reward / 2 # given to both estimator and adviser if appeal lost or no appeal
    appeal_cost = c(0.5)  # cost of appeal to estimator


class Subsession(BaseSubsession):
    def creating_session(self):
        print("Creating session.")
        playersList = []

        # get default group assignment
        for group in self.get_groups():
            players = group.get_players()
            for p in players:
                playersList.append(p)

        # assign players to customized groups
        groups_count = len(self.get_groups())
        i = 0
        for group in self.get_groups():
            players_in_group = [playersList[i]]
            j = i
            while j + groups_count < len(playersList):
                players_in_group.append(playersList[j + groups_count])
                j += groups_count
            group.set_players(players_in_group)
            group.choose_grid()
            i += 1

        # Disclosure Non-Disclosure Condition assignment - debug print
        print("Group matrix:")
        print(*self.get_group_matrix(), sep="\n")
          
        for i, group in enumerate(self.get_groups()):
            print('Group {}'.format(i))
            players = group.get_players()
            for p in players:
                if p.id_in_group % 2 == 1:
                    p.disclosure = True
                else:
                    p.disclosure = False
                print(p.role(), 'Disclosure' if p.disclosure else 'Non-disclosure', p.id_in_group, p.matched_adviser().id_in_group, p.matched_estimator().id_in_group, p.matched_judge().id_in_group)
            print("-----------")
        print('Finish creating session.')

class Group(BaseGroup):
    grid_number = models.IntegerField()
    correct_answer = models.IntegerField()
    grid_path = models.StringField()
    small_grid_path = models.StringField()

    example_grid_number = models.IntegerField()
    example_grid_path = models.StringField()
    example_grid_num_dots = models.StringField()
    example_small_grid_path = models.StringField()

    # Chooses a grid. Will choose a random grid-3x3_grid pair based on what is in the directory. Files must be named in this format: 
    # gridX_N.svg and small_gridX.svg, where X is a unique number per grid-3x3_grid pair, and N is the number of filled in dots in the entire grid.
    # Will assign values to group variables: grid_number, correct_answer, grid_path, small_grid_path.
    def choose_grid(self):
        static_dir = './study/static/study'
        static_files = os.listdir(static_dir)
        grid_choices = list(filter(lambda x: re.match(r"grid[0-9]*_[0-9]*\.svg", x), static_files))

        random.shuffle(grid_choices)

        self.grid_path = 'study/' + grid_choices.pop()
        self.grid_number = int(re.search(r"grid([0-9]*)_[0-9]*\.svg", self.grid_path).group(1))
        self.correct_answer = int(re.search(r"grid[0-9]*_([0-9]*)\.svg", self.grid_path).group(1))
        self.small_grid_path = 'study/small_grid' + str(self.grid_number) + '.svg'

        self.example_grid_path = 'study/' + grid_choices.pop()
        self.example_grid_number = int(re.search(r"grid([0-9]*)_[0-9]*\.svg", self.example_grid_path).group(1))
        self.example_grid_num_dots = self.example_grid_path[12:15]
        self.example_small_grid_path = 'study/small_grid' + str(self.example_grid_number) + '.svg'
        print("GridNum: ", self.example_grid_number, " GridPath: ", self.example_grid_path, " SmallGridPath: ", self.example_small_grid_path)

class Player(BasePlayer):
    appealed = models.BooleanField(
        label="Would you like to file an appeal?",
        choices=[
            [True, "Yes"],
            [False, "No"]
        ],
        widget=widgets.RadioSelect
    )
    appeal_granted = models.BooleanField(
        label= "What is your judgment?",
        choices=[
            [False, "The estimator and adviser should both receive " +
                str(Constants.appeal_reward_split) + "."],
            [True, "The estimator should receive " + str(Constants.appeal_reward) +
             " and the adviser should receive nothing."]
        ],
        widget=widgets.RadioSelect
    )

    grid_reward = models.CurrencyField(initial=c(0))
    entered_email = models.BooleanField()
    disclosure = models.BooleanField()

    email = models.StringField(
        label="Please provide your email address. We will send your payment as an Amazon.com gift card to this " +
              "email address within five business days.",
        blank=True,
        initial=""
    )

    consent18 = models.BooleanField(
        label="I am age 18 or older",
        widget=widgets.RadioSelect
    )
    consentRead = models.BooleanField(
        label="I have read and understand the above information",
        widget=widgets.RadioSelect
    )
    consentWant = models.BooleanField(
        label="I want to participate in this research and continue with this study",
        widget=widgets.RadioSelect
    )
    mTurkId = models.StringField(
        label="Please enter your Amazon MTurk ID to continue:",
        initial=""
    )

    # Demographic questions
    gender = models.IntegerField(
        label="What is your gender?",
        choices=[
            [1, 'Male'],
            [2, 'Female']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    age = models.IntegerField(
        label="What is your age?",
        min=18,
        max=130,
        blank=True
    )
    race = models.IntegerField(
        label="What is your race?",
        choices=[
            [1, 'White'],
            [2, 'Black, African-American'],
            [3, 'American Indian or Alaska Native'],
            [4, 'Asian or Asian-American'],
            [5, 'Pacific Islander'],
            [6, 'Multiple races or some other race']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    education = models.IntegerField(
        label="Please indicate the highest level of education completed.",
        choices=[
            [1, 'Grammar school'],
            [2, 'High school or equivalent'],
            [3, 'Vocational/technical school (2 year)'],
            [4, 'Some college'],
            [5, 'College graduate (4 year)'],
            [6, 'Master\'s degree (MS, etc.)'],
            [7, 'Doctoral degree (PhD, etc.)'],
            [8, 'Professional degree (MD, JD, etc.)'],
            [9, 'Other']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )
    income = models.IntegerField(
        label="Please indicate your current household income in U.S. dollars",
        choices=[
            [1, 'Under $10,000'],
            [2, '$10,000 - $19,999'],
            [3, '$20,000 - $29,999'],
            [4, '$30,000 - $39,999'],
            [5, '$40,000 - $49,999'],
            [6, '$50,000 - $74,999'],
            [7, '$75,000 - $99,999'],
            [8, '$100,000 - $150,000'],
            [9, 'Over $150,000']
        ],
        widget=widgets.RadioSelect,
        blank=True
    )

    recommendation = models.IntegerField(
        min=1,
        max=900,
        initial=None
    )

    estimate = models.IntegerField(
        min=1,
        max=900,
        initial=None
    )

    get_answer_wrong = models.BooleanField()

    timed_out = models.BooleanField(initial) 

    # Final Manipulation checks - No restrictions on answers to players - Role Independent
    manip_final_adviser_payment_question = models.BooleanField(
        widget=widgets.RadioSelect)
    manip_final_estimator_payment_question = models.BooleanField(
        widget=widgets.RadioSelect)
    manip_final_conflict_disclosed_or_not = models.BooleanField(
        widget=widgets.RadioSelect)

    # Initial Manipulation Questions - Players not allowed to proceed unless answered True
    manip_adv_adviser_payment_question = models.BooleanField(
        label="In the dots estimation task, you get a bonus only if the estimator underestimates the true number of solid dots.",
        widget=widgets.RadioSelect
    )

    manip_adv_estimator_payment_question = models.BooleanField(
        label="In the dots estimation task, the estimator gets a bigger bonus the more accurate his/her estimate is.",
        widget=widgets.RadioSelect
    )

    manip_adv_payment_scheme_disclosed = models.BooleanField(
        label="Your payment scheme is disclosed to the estimator in the online communication form.",
        widget=widgets.RadioSelect
    )

    manip_adv_payment_scheme_not_disclosed = models.BooleanField(
        label="Your payment scheme is NOT disclosed to the estimator in the online communication form.",
        widget=widgets.RadioSelect
    )

    manip_est_estimator_payment_question = models.BooleanField(
        label="In the dots estimation task, you will get a bigger bonus the more accurate your estimate is.",
        widget=widgets.RadioSelect
    )

    manip_adv_judge_payment_question = models.BooleanField(
      label="In the dots estimation task, the adviser gets a bonus only if the estimator underestimates the true number of solid dots.",
      widget=widgets.RadioSelect
    )

    manip_est_judge_payment_question = models.BooleanField(
        label="In the dots estimation task, the estimator gets a bigger bonus the more accurate his/her estimate is.",
        widget=widgets.RadioSelect
    )

    manip_judge_disclosure_question = models.StringField(
        label="Did estimators know that the advisers would get a bonus if they overestimated?",
        widget=widgets.RadioSelect,
        choices=[
            "No, they didn’t",
            "Yes, they did",
            "Some estimators were told and some were not told"
        ]
    )

    comment = models.LongStringField(
        label="Do you have any comments for the researchers? (Optional)", blank=True)

    estimator_appeal_question = models.LongStringField(blank=True)

    judge_bonus_awarded_clarify = judge_bonus_field(True)
    judge_bonus_not_awarded_clarify = judge_bonus_field(False)


    
    # Blame Questions - Estimator
    blame_EST_I_blame_myself_for_my_guess = make_Likert_agreement(
        "I blame myself for my guess.")
    blame_EST_I_blame_the_adviser_for_my_guess = make_Likert_agreement(
        "I blame the adviser for my guess.")
    blame_EST_I_have_a_legitimate_grievance_against_the_adviser = make_Likert_agreement(
        "I have a legitimate grievance against the adviser.")
    blame_EST_I_have_a_strong_case_if_I_choose_to_pursue_an_appeal = make_Likert_agreement(
        "I have a strong case if I choose to pursue an appeal.")
    blame_EST_I_believe_that_others_would_rule_in_my_favor = make_Likert_agreement(
        "I believe that others would rule in my favor on an appeal.")
    blame_EST_The_adviser_treated_me_fairly = make_Likert_agreement(
        "The adviser treated me fairly.")
    blame_EST_I_was_mistreated_by_the_adviser = make_Likert_agreement(
        "I was mistreated by the adviser.")
    blame_EST_I_deserve_to_receive_the_full_bonus = make_Likert_agreement(
        "I deserve to receive the full bonus of $2.00.")

    # Blame Questions - Judge
    blame_JUDGE_I_blame_the_estimator_for_their_guess = make_Likert_agreement(
        "I blame the estimator for their guess.")
    blame_JUDGE_I_blame_the_adviser_for_the_estimators_guess = make_Likert_agreement(
        "I blame the adviser for the estimator's guess.")
    blame_JUDGE_estimator_has_legitimate_grievance_against_adviser = make_Likert_agreement(
        "The estimator has a legitimate grievance against the adviser.")
    blame_JUDGE_estimator_has_a_strong_case_to_pursue_an_appeal = make_Likert_agreement(
        "The estimator has a strong case if he or she choses to pursue an appeal.")
    blame_JUDGE_I_believe_others_would_rule_in_estimators_favor = make_Likert_agreement(
        "I believe that others would rule in the estimator's favor on an appeal.")
    blame_JUDGE_The_adviser_treated_the_estimator_fairly = make_Likert_agreement(
        "The adviser treated the estimator fairly.")
    blame_JUDGE_The_estimator_was_mistreated_by_the_adviser = make_Likert_agreement(
        "The estimator was mistreated by the adviser.")
    blame_JUDGE_The_estimator_deserves_to_receive_the_full_bonus = make_Likert_agreement(
        "The estimator deserves to receive the full bonus of $2.00.")


    # 6-player Group - 1 triplet for disclosure and 1 triplet for non-disclosure conditions
    # define role
    def role(self):
        if 1 <= self.id_in_group <= 2:
            return 'adviser'
        elif 3 <= self.id_in_group <= 4:
            return 'estimator'
        elif 5 <= self.id_in_group <= 6:
            return 'judge'

    def matched_adviser(self):
        id = self.id_in_group - 1
        if self.is_adviser():
            return self
        elif self.is_estimator():
            return self.group.get_players()[id - 2]
        else:
            return self.group.get_players()[id - 4]

    def matched_estimator(self):
        id = self.id_in_group - 1
        if self.is_estimator():
            return self
        elif self.is_adviser():
            return self.group.get_players()[id + 2]
        else:
            return self.group.get_players()[id - 2]

    def matched_judge(self):
        id = self.id_in_group - 1
        if self.is_judge():
            return self
        elif self.is_adviser():
            return self.group.get_players()[id + 4]
        else:
            return self.group.get_players()[id + 2]

    def get_correct_answer(self):
        return self.group.correct_answer

    def is_adviser(self):
        return self.id_in_group in list(range(1, 3))

    def is_estimator(self):
        return self.id_in_group in list(range(3, 5))

    def is_judge(self):
        return self.id_in_group in list(range(5, 7))

    def get_recommendation(self):
        return self.matched_adviser().recommendation

    def get_estimate(self):
        return self.matched_estimator().estimate

    def number_off(self):
        return self.matched_estimator().estimate - self.group.correct_answer

    # Calculates rewards based on the adviser's recommendation and estimator's estimate, then stores them per player in %grid_reward%
    def calculate_grid_rewards(self):
        adviser = self.matched_adviser()
        estimator = self.matched_estimator()

        print('Calculate Grid Rewards - before \n', ' adviser: ', adviser.payoff, ' estimator: ', estimator.payoff)

        # (-inf, -40)
        if estimator.estimate < (self.group.correct_answer - 40):
            estimator.grid_reward = Constants.estimator_bonus_less_than_neg_40 
            adviser.grid_reward = Constants.adviser_bonus_less_than_10  
        
        # [-40, -10)
        elif (self.group.correct_answer - 40) <= estimator.estimate < (self.group.correct_answer - 10):
            estimator.grid_reward = Constants.estimator_bonus_within_neg_40_and_neg_10
            adviser.grid_reward = Constants.adviser_bonus_less_than_10  
        # [-10, 10]
        elif (self.group.correct_answer - 10) <= estimator.estimate <= (self.group.correct_answer + 10):
            estimator.grid_reward = Constants.estimator_bonus_within_neg_10_and_10
            adviser.grid_reward = Constants.adviser_bonus_within_neg_40_and_31  
        # (10, 40]
        elif (self.group.correct_answer - 10) < estimator.estimate <= (self.group.correct_answer + 40):
            estimator.grid_reward = Constants.estimator_bonus_within_10_and_40
            adviser.grid_reward = Constants.adviser_bonus_within_10_and_40
        # (40, inf)
        elif estimator.estimate > (self.group.correct_answer + 40):
            estimator.grid_reward = Constants.estimator_bonus_greater_than_40
            adviser.grid_reward = Constants.adviser_bonus_greater_than_40

        adviser.payoff = adviser.grid_reward
        estimator.payoff = estimator.grid_reward
        print('Calculate Grid Rewards - after\n', ' adviser: ', adviser.payoff, ' estimator: ', estimator.payoff)

    def recalculate_payOffs_with_appeal(self, appeal_granted):
        adviser = self.matched_adviser()
        estimator = self.matched_estimator()
        judge = self.matched_judge()

        print('In Recalculate. Payoffs - before\n', ' adviser: ', adviser.payoff, ' estimator: ', estimator.payoff, ' judge: ', judge.participant.payoff)

        if not estimator.appealed:
          adviser.payoff = adviser.grid_reward + Constants.appeal_reward_split
          estimator.payoff = estimator.grid_reward + Constants.appeal_reward_split
        else:
          if appeal_granted:
            adviser.payoff = adviser.grid_reward
            estimator.payoff = estimator.grid_reward + Constants.appeal_reward 
          else:
            adviser.payoff = adviser.grid_reward + Constants.appeal_reward_split
            estimator.payoff = estimator.grid_reward + Constants.appeal_reward_split - Constants.appeal_cost


        print('In Recalculate. Payoffs - after\n', ' adviser: ', adviser.payoff, ' estimator: ', estimator.payoff, ' judge: ', judge.participant.payoff)
    

    # Set Default Values for Recommendation and Estimate in times of unexpected failures in adviser and estimator rounds respectively
    def prep_before_decision(self):
        if self.is_estimator() or self.is_judge():
            if not self.matched_adviser().recommendation:
                self.matched_adviser().recommendation = self.group.correct_answer + (92 if self.disclosure else 28)
                print('Prep Recommendation', self.matched_adviser().recommendation)
        if self.is_judge():
            if not self.matched_estimator().estimate:
                self.matched_estimator().estimate = self.group.correct_answer + (46 if self.disclosure else 14)
                print('Prep Estimate', self.matched_estimator().estimate)
                self.calculate_grid_rewards()

    # Set Default Data for whole triplet group - for situations like timeout
    def set_timeout_data(self):
        self.timed_out = True
        if self.is_adviser():
            if self.recommendation is None or self.recommendation == 0:
                self.recommendation = self.group.correct_answer + \
                    (92 if self.disclosure else 28)
        elif self.is_estimator():
            if self.estimate is None or self.estimate == 0:
                self.estimate = self.group.correct_answer + \
                    (46 if self.disclosure else 14)
        elif self.is_judge():
            if self.matched_estimator().appealed:
                self.recalculate_payOffs_with_appeal(False)
