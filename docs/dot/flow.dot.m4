strict digraph {
	define(`graph_font_name', `fontname="Nimbus Mono"')

	graph [graph_font_name, truecolor=true bgcolor="#ff000000" ] /* splines=ortho unclear, separate splines unclear */
	node [graph_font_name]
	edge [graph_font_name]

	subgraph wholeg {
		subgraph init_login_keygen {
			init_node [label="init", shape=box, pos="0,0!"];
			init_ts_node [label="timestamp\ninit", shape=box, pos="0,-1!"];
			log_token_node [label="token\nlogin", shape=box, pos="1,0!"];
			gen_key_csr_node [label="token\ninit-keys", shape=box, pos="2.5,0!"];
			{ rank=same init_node log_token_node gen_key_csr_node }
		}

    subgraph separate_steps {
			subgraph separate_csr_download {
				download_csr_node [label="cert\ndownload-csrs", shape=box, style="dashed", pos="1.6,-1!"]
			}

			subgraph outside_certification {
				outside_cert_node [label="Sign CSRS at\napproved CA", style="dotted", shape=octagon, pos="4.1,-1!"];
			}
	  }

		subgraph cert_mng {
		  imp_cert_node [label="cert\nimport", shape=box, pos="0,-2!"];
		  reg_auth_node [label="cert\nregister", shape=box, pos="1.8,-2!"];
		  act_auth_node [label="cert\nactivate", shape=box, pos="3.5,-2!"];
			{ rank=same imp_cert_node reg_auth_node act_auth_node }
		}

		subgraph client_mng {
		  add_client_node [label="client\nadd", shape=box, pos="1.8,-3!"];
		  reg_client_node [label="client\nregister", shape=box, pos="0.8,-4!"];
		}

		subgraph ser_mng {
			add_serdesc_node [label="service\nadd-description", shape=box, pos="3,-4!"];
			enable_serdesc_node [label="service\nenable-description", shape=box, pos="0.3,-5!"];
			add_seraccess_node [label="service\nadd-access", shape=box, pos="2.2,-5!" ];
			upd_ser_node [label="service\nupdate-parameters", shape=box, pos="4.1,-5!"];
		}

		init_node -> init_ts_node;
		init_node -> log_token_node;
		log_token_node -> gen_key_csr_node

		imp_cert_node -> reg_auth_node
		reg_auth_node -> act_auth_node

		gen_key_csr_node -> download_csr_node [style=dashed]
		download_csr_node -> outside_cert_node [style=dotted]
		outside_cert_node -> imp_cert_node [style=dotted]

		/* gen_key_csr_node -> imp_cert_node */ /* Leave out to emphasize manual operations, bring back only with spline. */
		act_auth_node -> add_client_node:e
		add_client_node -> reg_client_node

		add_client_node -> add_serdesc_node
		add_serdesc_node -> enable_serdesc_node:n
		add_serdesc_node -> add_seraccess_node:n
		add_serdesc_node -> upd_ser_node:n
	}
}
