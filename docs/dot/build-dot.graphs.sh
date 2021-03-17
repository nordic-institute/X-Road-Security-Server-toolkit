#!/bin/bash

gen_flow_dot_imgs()
{
	local tmpdot
	tmpdot="$(mktemp)"
	m4 flow.dot.m4 > "${tmpdot}" && (
		neato -v -Tpng "${tmpdot}" -o ../img/flow.png
		neato -v -Tsvg "${tmpdot}" -o ../img/flow.svg
	)
	rm "${tmpdot}"
}

gen_flow_dot_imgs
