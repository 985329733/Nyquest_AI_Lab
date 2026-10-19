"""Full offline backup, including ignored toolchains and Git history."""
from pathlib import Path
from datetime import datetime, timezone, timedelta
import argparse,hashlib,json,os,re,zipfile

def backup(source,destination,keep):
    source=source.resolve();destination=destination.resolve()
    if destination==source or source in destination.parents:raise ValueError('Backup destination must be outside the source')
    if source.drive.lower()==destination.drive.lower():raise ValueError('Choose a different drive for disaster recovery')
    destination.mkdir(parents=True,exist_ok=True)
    stamp=datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S_%f')
    final=destination/f'jiuqi_{stamp}.zip';partial=destination/f'jiuqi_{stamp}.partial'
    paths=sorted(p for p in source.rglob('*') if p.is_file())
    manifest=[]
    try:
        with zipfile.ZipFile(partial,'x',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
            for p in paths:
                if p.is_symlink():raise ValueError(f'Explicit handling required for symbolic link: {p}')
                before=p.stat();digest=hashlib.sha256();name=p.relative_to(source).as_posix()
                with p.open('rb') as src,z.open('jiuqi/'+name,'w',force_zip64=True) as dst:
                    for data in iter(lambda:src.read(1024*1024),b''):digest.update(data);dst.write(data)
                after=p.stat()
                if (before.st_size,before.st_mtime_ns)!=(after.st_size,after.st_mtime_ns):raise ValueError(f'Source changed during backup: {p}')
                manifest.append({'path':name,'bytes':after.st_size,'sha256':digest.hexdigest()})
            z.writestr('BACKUP_MANIFEST.json',json.dumps(manifest,ensure_ascii=False,indent=2))
        with zipfile.ZipFile(partial) as z:
            if z.testzip() is not None:raise ValueError('Backup CRC verification failed')
            if len(z.namelist())!=len(paths)+1:raise ValueError('Backup file count mismatch')
            # Toolchain and Git are mandatory, including otherwise ignored files.
            names=z.namelist()
            for suffix in ('Tools/NYC_NY8/app/bin/sdcc.exe','Tools/NYASM/app/nylinker.exe','.git/HEAD'):
                if not any(n.endswith(suffix) for n in names):raise ValueError('Missing required backup content: '+suffix)
        partial.rename(final)
    except Exception:
        if partial.exists():partial.unlink()
        raise
    owned=sorted((p for p in destination.iterdir() if p.is_file() and re.fullmatch(r'jiuqi_\d{8}_\d{6}_\d{6}\.zip',p.name)),reverse=True)
    removed=[]
    for old in owned[keep:]:
        if old.resolve().parent!=destination:raise ValueError('Unsafe retention path')
        old.unlink();removed.append(old.name)
    result={'archive':str(final),'files':len(paths),'bytes':final.stat().st_size,'sha256':hashlib.sha256(final.read_bytes()).hexdigest(),'retained':min(len(owned),keep),'removed':removed,'verified':'ZIP CRC, file count, required toolchain and Git content; SHA256 manifest included'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--destination',type=Path,required=True);a.add_argument('--keep',type=int,default=10)
    n=a.parse_args()
    if not 1<=n.keep<=100:a.error('keep must be 1..100')
    backup(n.source,n.destination,n.keep)
