import os
import sys
import time
import random
from garminconnect import Garmin
from garmin_planner.__init__ import logger

class Client(object):
    def __init__(self, email, password, mfa_callback=None):
        self._email = email
        self._password = password
        
        def _default_mfa_callback():
            code = os.getenv("GARMIN_MFA_CODE")
            if not code:
                if sys.stdin.isatty():
                    return input("Enter MFA code: ")
                else:
                    raise Exception("GARMIN_MFA_CODE environment variable not set")
            return code
        
        self._mfa_callback = mfa_callback or _default_mfa_callback
        self._api = Garmin(email, password, prompt_mfa=self._mfa_callback)

        if not self.login():
            raise Exception("Login failed")
     
    def getAllWorkouts(self) -> dict:
        return self._api.get_workouts()

    def deleteWorkout(self, workout: dict) -> bool:
        res = self._api.delete_workout(workout['workoutId'])
        if res:
            logger.info(f"""Deleted workoutId: {workout['workoutId']} workoutName: {workout['workoutName']}""")
            return True
        else:
            logger.warn(f"""Could not delete workout. Workout not found with workoutId: {workout['workoutId']} (workoutName: {workout['workoutName']})""")
            return False

    def scheduleWorkout(self, id, date: str) -> bool:
        return self._api.schedule_workout(id, date)

    def importWorkout(self, workoutJson) -> dict:
        resJson = self._api.upload_workout(workoutJson)
        logger.info(f"""Imported workout {resJson['workoutName']}""")
        return resJson
    
    def login(self) -> bool:
        try:
            self._api.login()
            return True
        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False