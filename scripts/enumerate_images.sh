#!/bin/bash
x=1; for i in *.png; do counter=$(printf %03d $x); ln -s "$i" img"$counter".png; x=$(($x+1)); done
