S3是基于密钥/值的.所以没办法



There is no way to do this because there is no native support for `regex` in S3. You have to get the entire list and apply the search/regex at the client side. The only filtering option available in `list_objects` is by `prefix`.

[list_objects](http://boto3.readthedocs.io/en/latest/reference/services/s3.html#S3.Client.list_objects)

> Prefix (string) -- Limits the response to keys that begin with the specified prefix.

One option is to use the Python module `re` and apply it to the list of objects.



```py
import re
pattern = re.compile(<file_pattern_you_are_looking_for>)
for key in billing_bucket.list():
    if pattern.match(key.name):
        print key.name
```

