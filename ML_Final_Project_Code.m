% Machine Learning Final Project: Determining the Outcome of NBA Games
% By Matthew Smarsch and Frank Longueira

clear all;
close all;
clc;

%% Training Data Import and Set Generation

% Import Data From Excel into MATLAB
stats = 3:15;                % Column numbers of team stats per game being used as features
opp_stats = 3:14;            % Column numbers of opponent team stats per game being used as features                                                                              
num_seas = 6;                % Total number of seasons being used in our model
num_feat = length([stats opp_stats]);
seasons = cell(1,num_seas);

[~,~,Team_Train_Feats] = xlsread('NBA Data.xls','Team Features (Being Used)');     % Import features used during training
[~,~,Opp_Train_Feats] = xlsread('NBA Data.xls','Opponents Features (Being Used)'); % Import features used during training
[~,~,Test_Feats] = xlsread('NBA Data.xls','2014-15 Test Set');                     % Import features used during training
[~,~,Team_names] = xlsread('NBA Data.xls','Team Names 2014-15');                   % Import 2014-15 team names as strings   
        

work_names = {'2013-14' '2012-13' '2010-11' '2009-10' '2008-09' '2014-15 Test Set'};       % Worksheet names in Excel file for each NBA Season being used

for j1=1:num_seas             % Collect each season's worth of games/scores into the cell array seasons
    [~, ~, seasons{j1}] = xlsread('NBA Data.xls',work_names{j1});
end



% Generate Training Set of Features & Labels

features = cell(num_seas-1,1);
labels = cell(num_seas-1,1);

for i = 1:num_seas-1
    year = work_names{i};
    D = seasons{i};
    for ii = 2:max(size(D))
        away_team = D{ii,1};
        home_team = D{ii,3};
        feat_away = [cell2mat(Team_Train_Feats(find((strcmp(Team_Train_Feats(:,1),year)) & strcmp(Team_Train_Feats(:,2),away_team)), stats))];
        feat_home = [cell2mat(Team_Train_Feats(find((strcmp(Team_Train_Feats(:,1),year)) & strcmp(Team_Train_Feats(:,2),home_team)),stats))];
        opp_feat_away  = [cell2mat(Opp_Train_Feats(find((strcmp(Opp_Train_Feats(:,1),year)) & strcmp(Opp_Train_Feats(:,2),away_team)),opp_stats))];
        opp_feat_home = [cell2mat(Opp_Train_Feats(find((strcmp(Opp_Train_Feats(:,1),year)) & strcmp(Opp_Train_Feats(:,2),home_team)),opp_stats))];
        if cell2mat(D(ii,2)) > cell2mat(D(ii,4))
            label = 1;
        else
            label = 0;
        end
        
        feature_seas(ii-1,:) = [feat_away-feat_home opp_feat_away-opp_feat_home];
        label_seas(ii-1,1) = label;
        
    end
    features{i} = feature_seas;
    labels{i} = label_seas;
    
end

features = zscore(cell2mat(features));          % Normalize features
labels = cell2mat(labels);                              
M = length(labels);

%% Generate Test Set Features and Labels (2014-15 NBA Season)

% Importing season information

[Gnum, Gtxt, Graw] = xlsread('NBA Data.xls','201415games');
[Snum, Stxt, Sraw] = xlsread('NBA Data.xls','201415dataAvgs');

startInd = max(find(Gnum(:, 1) == 1 , 1, 'last'), find(Gnum(:, 3) == 1 , 1, 'last')) + 2;

% Get Validation Features

away_stats = [];
away_opp_stats = [];
home_stats = [];
home_opp_stats = [];
features_test = [];
oppColStart = 14;
for i = startInd:size(Graw, 1)
    away_ind = find(strcmp(Sraw(:,1), Graw(i,1)), 1, 'first');
    away_gp = Gnum(i-1, 1);
    home_ind = find(strcmp(Sraw(:,1), Graw(i,3)), 1, 'first');
    home_gp = Gnum(i-1, 3);
    away_stats = [Snum(away_ind+away_gp-1, 1:oppColStart-1)];
    away_opp_stats = [Snum(away_ind+away_gp-1, oppColStart:end)];
    home_stats = [Snum(home_ind+home_gp-1, 1:oppColStart-1)];
    home_opp_stats = [Snum(home_ind+home_gp-1, oppColStart:end)];
    features_test = [features_test; away_stats-home_stats, away_opp_stats-home_opp_stats];
end

features_test = zscore(features_test);                 % Normalize validation set features

% Get Test Feature Labels

labels_test = cell2mat(Test_Feats(startInd:end,7));    % Store validation set features


%% PCA Dimensionality Reduction
                                
[Eigvect, Evalues] = eig(cov(features));                       % Find eigenvalues/eigenvector of covariance matrix of normalized features                          
Evalues = diag(Evalues);                                       % Extract eigenvalues off of the diagonal 
opt = 0;

for d=1:num_feat                                               % Find number of eigenvectors that account for at least 95% of total variance
   x = sum(Evalues(d:end))/sum(Evalues);
   opt = d;
   if x > 0.95
       continue
   else
       opt = d-1;
       break
   end 
end

pca_features = (Eigvect(:,opt:end)'*features')';               % PCA transforms raw data into lower dimension
pca_valid = (Eigvect(:,opt:end)'*features_test')';             % PCA transforms raw data into lower dimension 

%% Linear Regression Classification

M_test = length(labels_test);                           % Number of data points in test set

X = [ones(length(pca_features),1) pca_features];        % Apply linear regression algorithm
X_tilde = pinv(X);
T = labels;
W = X_tilde*T;
LR_pre = (W(1) + pca_valid*W(2:end))> 0.5;   


LR_correct = 1-(sum(xor(LR_pre,labels_test))/M_test)    % Percentage of test set predictions correct using linear regression


%% K-Nearest Neighbors

k = ceil(sqrt(M));
KNN_pre = zeros(M_test,1);

for u = 1:M_test
    input = pca_valid(u,:);
    [IDX D] = knnsearch(pca_features,input,'K',k, 'NSMethod','euclidean','IncludeTies',true);
    A = cell2mat(IDX);
    KNN_pre(u) = round(mean(labels(A)));
end


KNN_correct = 1-(sum(xor(KNN_pre,labels_test))/M_test)              % Percentage of test set predictions correct using kNN

%% SVM Classification

% Used the following gridsearch with 10-fold cross validation to find optimal RBF parameters

% scale = [10e-5 10e-4 10e-3 10e-2 10e-1 10e0 10e1 10e2 10e3 10e4 10e5];
% box = [10e-5 10e-4 10e-3 10e-2 10e-1 10e0 10e1 10e2 10e3 10e4 10e5];
% store = zeros(length(scale),length(box));
% for k = 1:length(scale)
%     for u = 1:length(box)
%     SVMStruct = fitcsvm(features,labels,'BoxConstraint', box(u),'KernelFunction','RBF','KernelScale',scale(k));
%     error = kfoldLoss(crossval(SVMStruct));
%     store(k,u) = error;
%     end
% end
% 
% [loc_scale loc_box] = find(store == min(min(store)))
% 
% scale_best = scale(loc_scale)
% box_best = box(loc_box) 


% Best Scale Factor Attained = 12
% Best Box Constraint Attained = 0.1  
% Minimum Cross Validation Average Error = 0.2950

box_best = 0.1;
scale_best = 12;
SVMStruct = fitcsvm(features,labels,'BoxConstraint', box_best,'KernelFunction','RBF','KernelScale',scale_best);
SVM_pre = predict(SVMStruct, features_test);
SVM_correct = 1-(sum(xor(SVM_pre,labels_test))/M_test)

%% Autoencoder Classification ;)

[Y1 X1] = size(features_test);
[Y2 X2] = size(features);
cross_val = Y2-Y1;

hiddensize1 = 2; % Using a greedy gridsearch approach: optimal node size found to be 2, 
                 % WR = 0.1, SR = 4, SP = 0.25 with ~ 72% classification rate via cross validation
SP = 0.25;
SR = 4;
WR = 0.1;
    
autoenc1 = trainAutoencoder(features(1:cross_val,:)',hiddensize1, ...   % Pre-train single layer autoencoder
    'MaxEpochs',1000, ...
    'L2WeightRegularization',WR, ...
    'SparsityRegularization',SR, ...
    'SparsityProportion',SP, ...
    'ScaleData', false);

layer1_feat = encode(autoenc1,features(1:cross_val,:)');                        % Encode features using trained autoencoder layer

softnet = trainSoftmaxLayer(layer1_feat,labels(1:cross_val)','MaxEpochs',1000); % Pre-train softmax layer

deepnet = stack(autoenc1, softnet);                                     % Stack autoencoder and softmax layer together

deepnet.trainParam.epochs = 5000;                                       % Set epochs for entire network training

deepnet_trained = train(deepnet, features(1:cross_val,:)', labels(1:cross_val)');   % Fine-tune entire stacked network 

labels_pre = deepnet_trained(features(cross_val+1:end,:)');             % Use network to predict labels on a validation set

perform(deepnet_trained,labels(cross_val+1:end)',labels_pre);
plotconfusion(labels(cross_val+1:end)',labels_pre);
labels_pre = labels_pre > 0.5;

cross_val_correct = 1-(sum(xor(labels(cross_val+1:end)',labels_pre))/length(labels_pre));   % Percentage correct on validation set

% After finding optimal parameter using cross validation and finetuning, we
% apply the network to the test set:

labels_pre_test = deepnet_trained(features_test'); % Predict labels for test set
plotconfusion(labels_test',labels_pre_test)        % Confusion matrix generated
labels_pre_test = labels_pre_test > 0.5;           
AE_correct = 1-(sum(xor(labels_test',labels_pre_test))/length(labels_test)) % Calculation of classificaiton rate 
    


% On average, AE_correct = 71.8% (ran 25 times to account for probabilistic natures of initial weights.

    

    


                 