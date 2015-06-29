__author__ = 'joschlemper'import loggingimport osimport datastorage as storefrom simple_classifiers import SimpleClassifierfrom models.rbm import RBMfrom rbm_config import *from models.rbm_logger import *import kanade_loader as loaderdef find_associative_rbm_hyper_parameters():    proj_name = 'AssociativeRBM_params'    # Create project manager, loggers    manager = store.StorageManager(proj_name)    f = open('score.txt', 'wr')    logging.basicConfig(filename=proj_name+'.log', level=logging.INFO)    logging.info("Starting the project: " + proj_name)    # Load kanade database    mapping = {'anger': 'sadness', 'contempt': 'happy', 'disgust': 'sadness', 'fear': 'sadness', 'happy': 'happy', 'sadness': 'sadness', 'surprise': 'happy'}    train, valid, test = loader.load_kanade(n=100, set_name='sharp_equi25_25', pre={'scale2unit': True})    train_x, train_y = train    test_x, test_y = test    train01 = loader.sample_image(train_y, mapping=mapping)  # Sample associated image    train01_x, train01_y = train01 # Sample associated image    dataset01 = loader.load_kanade(n=100, set_name='sharp_equi25_25', emotions=['sadness','happy'], pre={'scale2unit': True})  # Target Image    # Create Classifier    clf = SimpleClassifier(classifier='logistic', train_x=dataset01[0][0], train_y=dataset01[0][1])    # AssociativeRBM Parameter    n_visible = train_x.get_value().shape[1]    n_visible2 = n_visible    sparsity_target_range = [0.01]  # [0.01, 0.001]    sparsity_cost_range = [0.5]    # histogram mean activities of the hidden units    sparsity_decay_range = [0.9]    n_hidden_range = [10, 50, 100, 200, 300, 500]    cd_types = [CLASSICAL, PERSISTENT]    cd_step_range = [1]    learning_rate_options = [0.01, 0.005, 0.001, 0.0005, 0.0001, 0.00001]    momentum_types = [CLASSICAL, NESTEROV]    momentum_range = [0.5, 0.9]  #[0.1, 0.5, 0.9]    weight_decay_range = [0.001, 0.0001, 0.01]# [0.0001, 0.0005, 0.001]    # sparsity_target_range = [0.1 ** 9, 0.1 ** 7, 0.00001, 0.001, 0.01]    # sparsity_cost_range = [0.01, 0.1, 0.5]    # histogram mean activities of the hidden units    # sparsity_decay_range = [0.9, 0.95, 0.99]    config = RBMConfig()    config.v_n = n_visible    config.v2_n = n_visible2    config.progress_logger = AssociationProgressLogger(img_shape=(25, 25))    # Iterate through parameters    possibilities = reduce(lambda x, y: x*y,                           map(lambda x: len(x), [n_hidden_range, cd_types, cd_step_range, learning_rate_options,                                                  momentum_types, momentum_range, weight_decay_range,                                                  sparsity_target_range, sparsity_cost_range, sparsity_decay_range]), 1)    logging.info(str(possibilities) + " parameter sets to explore")    # Keep track of the best one    classical_max_cost = - float('-inf')    persistent_max_cost = - float('-inf')    classical_max_name = ''    persistent_max_name = ''    counter = 1    for sd in sparsity_decay_range:        for sc in sparsity_cost_range:            for st in sparsity_target_range:                for cd_steps in cd_step_range:                    for mt in momentum_types:                        for m in momentum_range:                            for wd in weight_decay_range:                                for cd_type in cd_types:                                    for n_hidden in n_hidden_range:                                        for lr in learning_rate_options:                                            # Initialise the RBM and training parameters                                            logging.info("Search Progress: {} / {}".format(str(counter), possibilities))                                            counter += 1                                            tr = TrainParam(learning_rate=lr,                                                            momentum_type=mt,                                                            momentum=m,                                                            weight_decay=wd,                                                            sparsity_constraint=False,                                                            sparsity_target=st,                                                            sparsity_cost=sc,                                                            sparsity_decay=sd)                                            config.h_n = n_hidden                                            config.associative = True                                            config.train_params = tr                                            config.cd_type = cd_type                                            config.cd_steps = cd_steps                                            rbm = RBM(config)                                            if os.path.isdir(os.path.join('data', proj_name, str(rbm))):                                                logging.info("Skipping {} as it was already sampled".format(rbm))                                                continue                                                                                manager.move_to(str(rbm))                                            converged=False                                            min_cost = - float('-inf')                                            for j in xrange(0, 5):                                                # Train RBM - learn joint distribution                                                try:                                                    curr_cost = rbm.train(train_x, train01_x)                                                    if min_cost < np.min(curr_cost):                                                        # No longer improves                                                        logging.info('Converged, moving on')                                                        break                                                    min_cost = min(np.min(curr_cost), min_cost)                                                except Exception as inst:                                                    logging.info(inst)                                                    break                                                # manager.persist(rbm)                                                print "... reconstruction of associated images"                                                reconstructed_tr = rbm.reconstruct_association(train_x, train01_x, 5, 0, plot_n=10, img_name='{}_recon_orig_{}.png'.format(j, rbm))                                                reconstructed_y = rbm.reconstruct_association(test_x, None, 5, 0, plot_n=10, img_name='{}_recon_{}.png'.format(j, rbm))                                                print "... reconstructed"                                                # Classify the reconstructions                                                score_orig = clf.get_score(reconstructed_y, test_y.eval())                                                clf.retrain(reconstructed_tr, train01_y.eval())                                                score_retrain = clf.get_score(reconstructed_y, test_y.eval())                                                out_msg = '{} (orig, retrain):{},{}'.format(rbm, score_orig, score_retrain)                                                logging.info(out_msg)                                                print out_msg                                                f.write(out_msg + '\n')                                                # print str(rbm)                                            manager.move_to_project_root()    logging.info("End of finding parameters")    f.close()if __name__ == '__main__':    find_associative_rbm_hyper_parameters()