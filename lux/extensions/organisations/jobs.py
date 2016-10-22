from pq import api

from .forms import MemberRole


@api.job()
def organisation_owners(self):
    """Check that each organisation has at least one owner
    """
    manager = self.backend.app
    odm = manager.odm()
    modified = []
    with odm.begin() as session:
        superuser = session.query(odm.user).filter_by(superuser=True).first()
        for org in session.query(odm.organisation).all():
            members = org.members
            ok = False
            for member in members:
                if member.role == MemberRole.owner:
                    ok = True
                    break
            if ok:
                continue

            # pick the first member
            for member in members:
                if member.role == MemberRole.member:
                    member.role = MemberRole.owner
                    session.add(member)
                    session.flush()
                    modified.append(org.username)
                    ok = True
                    break
            if ok:
                continue

            # pick one
            if members:
                member = members[0]
                member.role = MemberRole.owner
                session.add(member)
                session.flush()
                modified.append(org.username)
                continue

            member = odm.orgmember(
                organisation=org,
                user=superuser,
                role=MemberRole.owner,
                private=True
            )
            modified.append(org.username)
            session.add(member)
            session.flush()

    return modified
