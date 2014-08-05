from zope.component import getMultiAdapter

from trac import core
from trac.perm import IPermissionStore, DefaultPermissionStore, IPermissionGroupProvider

from penelope.core.security.acl import IRoleFinder
from penelope.core.dbsession import DBSession
from penelope.models import Project, User

 
class PorPermissionStore(DefaultPermissionStore):
    """ """
    core.implements(IPermissionStore, IPermissionGroupProvider)

    # IPermissionGroupProvider
    def get_permission_groups(self, username):
        # TODO: work only for por/trac on the same wsgi stack
        project_id = self.env.config.get('por-dashboard', 'project-id')
        if project_id:
            project = DBSession().query(Project).get(project_id)
            user = DBSession().query(User).filter_by(email=username).first()
            if user:
                return list(getMultiAdapter((project, user), IRoleFinder).get_roles())
        return list() 

    # IPermissionStore
    def get_user_permissions(self, username):
        """Return all permissions for the user with the specified name.

        The permissions are returned as a dictionary where the key is the name
        of the permission, and the value is either `True` for granted
        permissions or `False` for explicitly denied permissions."""

        # TODO: work only for por/trac on the same wsgi stack
        actions = set(super(PorPermissionStore, self).get_user_permissions(username))
        project_id = self.env.config.get('por-dashboard', 'project-id')
        if project_id:
            project = DBSession().query(Project).get(project_id)
            user = DBSession().query(User).filter_by(email=username).first()
            if user:
                for role in getMultiAdapter((project, user), IRoleFinder).get_roles():
                    actions.update(set(super(PorPermissionStore, self).get_user_permissions(role)))
        return list(actions) 
