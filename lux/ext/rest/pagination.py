from pulsar.utils.httpurl import iri_to_uri


class Pagination:

    def first_link(self, request, total, limit, offset):
        n = self._count_part(offset, limit, 0)
        if n:
            offset -= n*limit
        if offset > 0:
            return self.link(request, 0, min(limit, offset))

    def prev_link(self, request, total, limit, offset):
        if offset:
            olimit = min(limit, offset)
            prev_offset = offset - olimit
            return self.link(request, prev_offset, olimit)

    def next_link(self, request, total, limit, offset):
        next_offset = offset + limit
        if total > next_offset:
            return self.link(request, next_offset, limit)

    def last_link(self, request, total, limit, offset):
        n = self._count_part(total, limit, offset)
        if n > 0:
            return self.link(request, offset + n*limit, limit)

    def link(self, request, offset, limit):
        params = request.url_data.copy()
        cfg = request.config
        params.update({cfg['API_OFFSET_KEY']: offset,
                       cfg['API_LIMIT_KEY']: limit})
        location = iri_to_uri(request.path, params)
        return request.absolute_uri(location)

    def __call__(self, request, result, total=None, limit=None, offset=None):
        if total is None:
            total = len(result)
            offset = 0
            limit = total or 1
        data = {
            'total': total,
            'result': result
        }
        first = self.first_link(request, total, limit, offset)
        if first:
            data['first'] = first
            prev = self.prev_link(request, total, limit, offset)
            if prev != first:
                data['prev'] = prev

        next = self.next_link(request, total, limit, offset)
        if next:
            last = self.last_link(request, total, limit, offset)
            if last != next:
                data['next'] = next
            data['last'] = last
        return data

    def _count_part(self, total, limit, offset):
        n = (total - offset) // limit
        # make sure we account for perfect matching
        if n*limit + offset == total:
            n -= 1
        return max(0, n)


class GithubPagination(Pagination):
    '''Github style pagination
    '''
    def __call__(self, request, result, total, limit, offset):
        links = []
        first = self.first_link(request, total, limit, offset)
        if first:
            links.append(first)
            prev = self.prev_link(request, total, limit, offset)
            if prev != first:
                links.append(prev)
        next = self.next_link(request, total, limit, offset)
        if next:
            last = self.last_link(request, total, limit, offset)
            if last != next:
                links.append(next)
            links.append(last)
        request.response['links'] = links
        return result
