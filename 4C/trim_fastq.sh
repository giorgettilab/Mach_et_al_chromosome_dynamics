#!/bin/bash

function usage {
    echo -e "usage : trim_fastq.sh -i INPUT [-l LEAVE] [-s START] [-e END]  [-h]"
    echo -e "Use option -h|--help for more information"
}

function help {
    echo
    echo "trim fastq files"
    echo "---------------"
    echo "OPTIONS"
    echo
    echo "   -i|--input INPUT : fastq.gz file to be trimmed"
    echo "   [-l|--leave LEAVE] : number of basepairs to be kept at the beginning of reads, NO COMPATIBLE WITH OTHER MODES"
    echo "   [-e|--end END] : number of basepairs to be trimmed at the end, NO COMPATIBLE WITH OTHER MODES"
    echo "   [-s|--start START] : number of basepairs to be trimmed at the beginning, NO COMPATIBLE WITH OTHER MODES"
    echo "   [-h|--help]: help"
    exit;
}



for arg in "$@"; do
  shift
  case "$arg" in
      "--input") set -- "$@" "-i" ;;
      "--start") set -- "$@" "-s" ;;
      "--end") set -- "$@" "-e" ;;
      "--leave") set -- "$@" "-l" ;;
      "--help")   set -- "$@" "-h" ;;
       *)        set -- "$@" "$arg"
  esac
done

INPUT=""
START=0
END=0
LEAVE=0

while getopts ":i:l:e:s:h" OPT
do
    case $OPT in
        i) INPUT=$OPTARG;;
	s) START=$OPTARG;;
	e) END=$OPTARG;;
	l) LEAVE=$OPTARG;;
        h) help ;;
        \?)
            echo "Invalid option: -$OPTARG" >&2
            usage
            exit 1
            ;;
        :)
            echo "Option -$OPTARG requires an argument." >&2
            usage
            exit 1
            ;;
    esac
done

echo "INPUT: $INPUT"
echo "number of bps to be trimmed at beginning (0 = inactive): $START"
echo "number of bps to be trimmed at the end (0 = inactive): $END"
echo "number of bps to be left at beginning (0 = inactive): $LEAVE"


if [ $# -lt 4 ]
then
    usage
    exit
fi


if [ $# -gt 7 ]; then

	usage
	exit

fi

if ! [ -f $INPUT ]; then

	echo "Input file does not exists!"
	exit
fi

name=`echo $INPUT | sed 's,.gz,,g'`

	if ! [ -f trimmed.$INPUT ]; then
	zcat $INPUT | awk 'BEGIN{
			
			s="'"$START"'"+0.
			e="'"$END"'"+0.
			l="'"$LEAVE"'"+0.

		}{
			tot++

			a=$0
			getline
			b=$0
			getline
			c=$0
			getline
			d=$0
			
			if(l!=0){
				tread=substr(b,1,l)		
				tquality=substr(d,1,l) 

				print a > "trimmed.""'"$name"'" 
                                print tread > "trimmed.""'"$name"'" 
                                print c > "trimmed.""'"$name"'" 
                                print tquality > "trimmed.""'"$name"'" 
			}


			if(s!=0){
                                tread=substr(b,s+1,length(b))             
                                tquality=substr(d,s+1,length(d))
				print a > "trimmed.""'"$name"'" 
                                print tread > "trimmed.""'"$name"'" 
                                print c > "trimmed.""'"$name"'" 
                                print tquality > "trimmed.""'"$name"'"  

                        }

			if(e!=0){
				tread=substr(b,1,length(b)-e)             
                                tquality=substr(d,1,length(d)-e)
                                print a > "trimmed.""'"$name"'" 
                                print tread > "trimmed.""'"$name"'" 
                                print c > "trimmed.""'"$name"'" 
                                print tquality > "trimmed.""'"$name"'"  	

			}
		}'
		
	fi

