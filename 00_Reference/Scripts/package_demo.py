"""Package a current verified project with its exact source and build evidence."""
from pathlib import Path
from datetime import datetime
import argparse
import hashlib
import json
import zipfile
from verification_contract import load_build_context, load_profile, read_json, sha256, validate_behavior, write_json


def package(project):
    project=Path(project).resolve()
    workflow=read_json(project/'Workflow_Verification.json')
    context,_=load_build_context(project)
    profile=load_profile(project)
    if workflow.get('Status')!='PASS' or workflow.get('context')!=context:
        raise ValueError('Package requires the current successful workflow')
    validate_behavior(read_json(project/'Behavior_Verification.json'),context,profile['behavior']['required_checks'])
    names=set(context['inputs'])
    stem=Path(context['binary']).stem
    names.update(stem+ext for ext in ('.bin','.elf','.map','.link.lst'))
    names.update(['Build_Context.json','Build_Verification.json','Configuration_Readback.json','Behavior_Verification.json','Workflow_Verification.json','build.log'])
    for name in ('README_For_Engineer.md','Bench_Results.md','Product_Requirements.md'):
        if (project/name).is_file(): names.add(name)
    payload={name:(project/name).read_bytes() for name in sorted(names)}
    manifest=[{'path':n,'sha256':hashlib.sha256(v).hexdigest(),'bytes':len(v)} for n,v in payload.items()]
    payload['MANIFEST_SHA256.json']=json.dumps(manifest,indent=2).encode('utf-8')
    output=project/'Delivery';output.mkdir(exist_ok=True)
    archive=output/(stem+'_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f')+'.zip')
    with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
        for name,data in payload.items():z.writestr(name,data)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:raise ValueError('Package CRC must verify')
        for entry in manifest:
            if hashlib.sha256(z.read(entry['path'])).hexdigest()!=entry['sha256']:
                raise ValueError('Package hashes must match source evidence')
    result={'status':'PASS','archive':str(archive),'sha256':sha256(archive),'firmware_sha256':context['binary_sha256'],'files':len(payload),'bench':'UNTESTED'}
    write_json(archive.with_suffix('.json'),result)
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project',type=Path)
    package(parser.parse_args().project)
