docker volume create \
	--driver local \
	--opt type=nfs \
	--opt o=addr=192.168.1.1,rw,tcp,nolock,rsize=4096,wsize=4096 \
	--opt device=:/alidata/nfs \
	nfs
