from hmac import digest_size
import uu
import requests
import hashlib
import uuid
import datetime as dt

sourceURL = "https://www.nytimes.com"
sourceTimestamp = str(dt.datetime.now()) #records timestamp of
sourceUUID = uuid.uuid4()
print(f"Password was generated at {sourceTimestamp} with {sourceURL} and {sourceUUID}")

#Password Generator -- uses website; adds uuid; hashes to produce password with high entropy

#Initial parameters -- websource (as request content bytes object); sourceUUID_asBytes (uuid bytes object)
websource = requests.get(sourceURL)
websourceContent = websource.content
sourceUUID_asBytes = sourceUUID.bytes
hashConcat = websourceContent + sourceUUID_asBytes

#Hash object parameters -- hashObj (hashlib object hashing with sha256)
hashObj = hashlib.blake2b(digest_size=15)
hashObj.update(hashConcat)

#Display password
print(hashObj.hexdigest())


