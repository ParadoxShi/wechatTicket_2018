from codex.baseerror import *
from codex.baseview import APIView

from wechat.models import User
from wechat.models import Activity


class UserBind(APIView):

    def validate_user(self):
        """
        input: self.input['student_id'] and self.input['password']
        raise: ValidateError when validating failed
        """
        if(user.student_id == self.input['openid']
            && user.password == self.input['password']):
            return
        else:
            raise NotImplementedError('You should implement UserBind.validate_user method')
            return

    def get(self):
        self.check_input('openid')
        return User.get_by_openid(self.input['openid']).student_id

    def post(self):
        self.check_input('openid', 'student_id', 'password')
        user = User.get_by_openid(self.input['openid'])
        self.validate_user()
        user.student_id = self.input['student_id']
        user.save()

class ActivityDetail(APIView):

    def activity_realised(self):
        if(activity.status == STATUS_PUBLISHED):
            return
        else:
            raise NotImplementedError('The Activity has not published')
            return

    def get(self):
        self.check_input('key')
        activity = Activity.get_by_key(self.input['key'])
        self.activity_realised()
        return {'name':activity.name, 'key':activity.key}#and so on