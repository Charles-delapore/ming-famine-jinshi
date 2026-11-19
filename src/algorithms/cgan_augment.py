import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import pairwise_distances
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler


class TabSynDex:
    def __init__(self):
        self.scores = {}

    def _basic_statistics_score(self, real_data, synth_data):
        n_cols = real_data.shape[1]
        scores = []
        for col_idx in range(n_cols):
            real_col = real_data[:, col_idx]
            synth_col = synth_data[:, col_idx]
            real_mean = np.mean(real_col)
            synth_mean = np.mean(synth_col)
            real_std = np.std(real_col)
            synth_std = np.std(synth_col)
            real_median = np.median(real_col)
            synth_median = np.median(synth_col)

            e_mean = min(abs(real_mean - synth_mean) / (abs(real_mean) + 1e-8), 1.0)
            e_std = min(abs(real_std - synth_std) / (abs(real_std) + 1e-8), 1.0)
            e_median = min(abs(real_median - synth_median) / (abs(real_median) + 1e-8), 1.0)
            scores.append((1 - e_mean + 1 - e_std + 1 - e_median) / 3)

        return np.mean(scores)

    def _correlation_score(self, real_data, synth_data):
        real_corr = np.corrcoef(real_data.T)
        synth_corr = np.corrcoef(synth_data.T)

        n = real_corr.shape[0]
        mask = ~np.eye(n, dtype=bool)
        real_vals = real_corr[mask]
        synth_vals = synth_corr[mask]

        def signed_log(x):
            return np.sign(x) * np.log(np.abs(x) + 1e-10)

        real_log = signed_log(real_vals)
        synth_log = signed_log(synth_vals)

        errors = np.abs(real_log - synth_log) / (np.abs(real_log) + 1e-8)
        errors = np.clip(errors, 0, 1)
        return 1 - np.mean(errors)

    def _propensity_mse_score(self, real_data, synth_data):
        n_real = len(real_data)
        n_synth = len(synth_data)

        combined = np.vstack([real_data, synth_data])
        labels = np.concatenate([np.zeros(n_real), np.ones(n_synth)])

        try:
            clf = LogisticRegression(max_iter=500, solver='lbfgs')
            clf.fit(combined, labels)
            probs = clf.predict_proba(combined)[:, 1]
            c = 0.5
            pmse = np.mean((probs - c) ** 2)
            max_pmse = 0.25
            score = 1 - min(pmse / max_pmse, 1.0)
        except Exception:
            score = 0.0

        return score

    def _support_coverage_score(self, real_data, synth_data, n_bins=10):
        n_cols = real_data.shape[1]
        coverages = []
        for col_idx in range(n_cols):
            real_col = real_data[:, col_idx]
            synth_col = synth_data[:, col_idx]

            bins = np.linspace(real_col.min(), real_col.max(), n_bins + 1)
            real_hist, _ = np.histogram(real_col, bins=bins)
            synth_hist, _ = np.histogram(synth_col, bins=bins)

            real_support = real_hist > 0
            if real_support.sum() == 0:
                coverages.append(0.0)
                continue

            covered = np.sum(real_support & (synth_hist > 0))
            coverage = covered / real_support.sum()
            coverages.append(coverage)

        return np.mean(coverages)

    def _ml_efficacy_score(self, real_data, synth_data, real_labels=None):
        if real_labels is None:
            return 0.5

        from sklearn.ensemble import RandomForestClassifier
        from sklearn.metrics import accuracy_score
        from sklearn.model_selection import train_test_split

        try:
            X_train_real, X_test, y_train_real, y_test = train_test_split(
                real_data, real_labels, test_size=0.3, random_state=42
            )

            n_synth = min(len(synth_data), len(X_train_real))
            X_train_synth = synth_data[:n_synth]
            y_train_synth = real_labels[:n_synth] if len(real_labels) >= n_synth else None

            clf_real = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
            clf_real.fit(X_train_real, y_train_real)
            acc_real = accuracy_score(y_test, clf_real.predict(X_test))

            if y_train_synth is not None:
                clf_synth = RandomForestClassifier(n_estimators=50, random_state=42, max_depth=5)
                clf_synth.fit(X_train_synth, y_train_synth)
                acc_synth = accuracy_score(y_test, clf_synth.predict(X_test))
                score = 1 - abs(acc_real - acc_synth)
            else:
                score = 0.5

        except Exception:
            score = 0.5

        return score

    def evaluate(self, real_data, synth_data, real_labels=None):
        real = np.asarray(real_data, dtype=np.float64)
        synth = np.asarray(synth_data, dtype=np.float64)

        n_cols = min(real.shape[1], synth.shape[1])
        real = real[:, :n_cols]
        synth = synth[:, :n_cols]

        nan_mask_real = ~np.any(np.isnan(real), axis=1)
        nan_mask_synth = ~np.any(np.isnan(synth), axis=1)
        real = real[nan_mask_real]
        synth = synth[nan_mask_synth]

        if len(real) == 0 or len(synth) == 0:
            return 0.0, {}

        s_basic = self._basic_statistics_score(real, synth)
        s_corr = self._correlation_score(real, synth)
        s_pmse = self._propensity_mse_score(real, synth)
        s_coverage = self._support_coverage_score(real, synth)
        s_ml = self._ml_efficacy_score(real, synth, real_labels)

        self.scores = {
            'basic_statistics': float(s_basic),
            'correlation': float(s_corr),
            'propensity_mse': float(s_pmse),
            'support_coverage': float(s_coverage),
            'ml_efficacy': float(s_ml),
        }

        tabsyndex = np.mean([s_basic, s_corr, s_pmse, s_coverage, s_ml])
        return float(tabsyndex), self.scores


class GMMEncoder:
    def __init__(self, n_modes=5):
        self.n_modes = n_modes
        self.gmms = {}
        self.scalers = {}

    def fit(self, data, col_indices):
        for idx in col_indices:
            col_data = data[:, idx].reshape(-1, 1)
            scaler = StandardScaler()
            scaled = scaler.fit_transform(col_data)
            n_modes = min(self.n_modes, len(np.unique(col_data)))
            n_modes = max(n_modes, 1)
            gmm = GaussianMixture(n_components=n_modes, random_state=42)
            gmm.fit(scaled)
            self.gmms[idx] = gmm
            self.scalers[idx] = scaler
        return self

    def encode(self, data, col_indices):
        encoded_parts = []
        for idx in range(data.shape[1]):
            if idx in self.gmms:
                col_data = data[:, idx].reshape(-1, 1)
                scaled = self.scalers[idx].transform(col_data)
                probs = self.gmms[idx].predict_proba(scaled)
                values = scaled.flatten()
                encoded_parts.append(np.hstack([probs, values.reshape(-1, 1)]))
            else:
                encoded_parts.append(data[:, idx:idx + 1])
        return np.hstack(encoded_parts)

    def decode(self, encoded, col_indices, encoded_dims):
        decoded = np.zeros((encoded.shape[0], len(col_indices)))
        offset = 0
        for i, idx in enumerate(col_indices):
            if idx in self.gmms:
                n_modes = self.gmms[idx].n_components
                probs = encoded[:, offset:offset + n_modes]
                values = encoded[:, offset + n_modes]
                mode_idx = np.argmax(probs, axis=1)
                decoded[:, i] = self.scalers[idx].inverse_transform(
                    values.reshape(-1, 1)
                ).flatten()
                offset += n_modes + 1
            else:
                decoded[:, i] = encoded[:, offset]
                offset += 1
        return decoded


class CGANDataAugmentor:
    def __init__(self, feature_cols, condition_col, noise_dim=32,
                 gen_layers=None, disc_layers=None,
                 learning_rate=0.001, epochs=2000, batch_size=128,
                 use_gmm_encoding=True, gmm_n_modes=5,
                 use_tabsyndex=True):
        self.feature_cols = feature_cols
        self.condition_col = condition_col
        self.noise_dim = noise_dim
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.batch_size = batch_size
        self.gen_layers = gen_layers or [128, 128, 64]
        self.disc_layers = disc_layers or [128, 128, 64]
        self.scaler = StandardScaler()
        self.generator = None
        self.discriminator = None
        self._tf_available = None
        self.use_gmm_encoding = use_gmm_encoding
        self.gmm_n_modes = gmm_n_modes
        self.use_tabsyndex = use_tabsyndex
        self.gmm_encoder = None
        self.tabsyndex_evaluator = TabSynDex() if use_tabsyndex else None

    def _check_tf(self):
        if self._tf_available is None:
            try:
                import tensorflow as tf
                self._tf_available = True
                self._tf = tf
            except ImportError:
                try:
                    import torch
                    import torch.nn as nn
                    self._tf_available = False
                    self._torch = torch
                    self._nn = nn
                except ImportError:
                    raise ImportError("需要安装 tensorflow 或 pytorch 来使用CGAN数据增强")
        return self._tf_available

    def _build_tf_model(self, input_dim, cond_dim, layers, output_dim=None, is_generator=True):
        tf = self._tf
        model = tf.keras.Sequential()
        model.add(tf.keras.layers.InputLayer(input_shape=(input_dim + cond_dim,)))
        for i, units in enumerate(layers):
            model.add(tf.keras.layers.Dense(units))
            model.add(tf.keras.layers.BatchNormalization())
            model.add(tf.keras.layers.LeakyReLU(0.2))
            if i < len(layers) - 1:
                model.add(tf.keras.layers.Dropout(0.1))
        if output_dim is None:
            output_dim = input_dim
        if is_generator:
            model.add(tf.keras.layers.Dense(output_dim, activation='linear'))
        else:
            model.add(tf.keras.layers.Dense(1, activation='sigmoid'))
        return model

    def _train_tf(self, features, conditions):
        tf = self._tf
        features_scaled = self.scaler.fit_transform(features)
        cond_values = conditions.values.reshape(-1, 1)
        cond_scaler = StandardScaler()
        cond_scaled = cond_scaler.fit_transform(cond_values)
        self._cond_scaler = cond_scaler

        if self.use_gmm_encoding:
            self.gmm_encoder = GMMEncoder(n_modes=self.gmm_n_modes)
            cont_indices = list(range(features_scaled.shape[1]))
            self.gmm_encoder.fit(features_scaled, cont_indices)
            features_encoded = self.gmm_encoder.encode(features_scaled, cont_indices)
            feature_dim = features_encoded.shape[1]
            self._feature_dim_raw = features_scaled.shape[1]
        else:
            features_encoded = features_scaled
            feature_dim = features_scaled.shape[1]

        cond_dim = 1

        self.generator = self._build_tf_model(
            self.noise_dim, cond_dim, self.gen_layers, feature_dim, is_generator=True
        )
        self.discriminator = self._build_tf_model(
            feature_dim, cond_dim, self.disc_layers, 1, is_generator=False
        )

        gen_optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.5)
        disc_optimizer = tf.keras.optimizers.Adam(learning_rate=self.learning_rate, beta_1=0.5)

        bce = tf.keras.losses.BinaryCrossentropy()

        dataset = tf.data.Dataset.from_tensor_slices(
            (features_encoded.astype(np.float32), cond_scaled.astype(np.float32))
        ).shuffle(10000).batch(self.batch_size)

        for epoch in range(self.epochs):
            d_losses = []
            g_losses = []
            for real_features, real_conds in dataset:
                batch_size = real_features.shape[0]
                noise = tf.random.normal([batch_size, self.noise_dim])
                gen_input = tf.concat([noise, real_conds], axis=1)
                fake_features = self.generator(gen_input, training=True)

                disc_real_input = tf.concat([real_features, real_conds], axis=1)
                disc_fake_input = tf.concat([fake_features, real_conds], axis=1)

                with tf.GradientTape() as disc_tape:
                    real_output = self.discriminator(disc_real_input, training=True)
                    fake_output = self.discriminator(disc_fake_input, training=True)
                    disc_loss = 0.5 * (
                        bce(tf.ones_like(real_output) * 0.9, real_output) +
                        bce(tf.zeros_like(fake_output) + 0.1, fake_output)
                    )
                disc_grads = disc_tape.gradient(disc_loss, self.discriminator.trainable_variables)
                disc_optimizer.apply_gradients(zip(disc_grads, self.discriminator.trainable_variables))

                with tf.GradientTape() as gen_tape:
                    noise = tf.random.normal([batch_size, self.noise_dim])
                    gen_input = tf.concat([noise, real_conds], axis=1)
                    fake_features = self.generator(gen_input, training=True)
                    disc_fake_input = tf.concat([fake_features, real_conds], axis=1)
                    fake_output = self.discriminator(disc_fake_input, training=True)
                    gen_loss = bce(tf.ones_like(fake_output), fake_output)
                gen_grads = gen_tape.gradient(gen_loss, self.generator.trainable_variables)
                gen_optimizer.apply_gradients(zip(gen_grads, self.generator.trainable_variables))

                d_losses.append(disc_loss.numpy())
                g_losses.append(gen_loss.numpy())

            if (epoch + 1) % 500 == 0:
                avg_d = np.mean(d_losses)
                avg_g = np.mean(g_losses)
                print(f"  CGAN Epoch {epoch+1}/{self.epochs}, G_loss: {avg_g:.4f}, D_loss: {avg_d:.4f}")

    def _train_torch(self, features, conditions):
        torch = self._torch
        nn = self._nn

        features_scaled = self.scaler.fit_transform(features)
        cond_values = conditions.values.reshape(-1, 1)
        cond_scaler = StandardScaler()
        cond_scaled = cond_scaler.fit_transform(cond_values)
        self._cond_scaler = cond_scaler

        if self.use_gmm_encoding:
            self.gmm_encoder = GMMEncoder(n_modes=self.gmm_n_modes)
            cont_indices = list(range(features_scaled.shape[1]))
            self.gmm_encoder.fit(features_scaled, cont_indices)
            features_encoded = self.gmm_encoder.encode(features_scaled, cont_indices)
            feature_dim = features_encoded.shape[1]
            self._feature_dim_raw = features_scaled.shape[1]
        else:
            features_encoded = features_scaled
            feature_dim = features_scaled.shape[1]

        cond_dim = 1

        class Generator(nn.Module):
            def __init__(self, noise_dim, cond_dim, layers, output_dim):
                super().__init__()
                dims = [noise_dim + cond_dim] + layers + [output_dim]
                self.net = nn.Sequential()
                for i in range(len(dims) - 2):
                    self.net.add_module(f'fc{i}', nn.Linear(dims[i], dims[i+1]))
                    self.net.add_module(f'bn{i}', nn.BatchNorm1d(dims[i+1]))
                    self.net.add_module(f'lrelu{i}', nn.LeakyReLU(0.2))
                    if i < len(layers) - 1:
                        self.net.add_module(f'drop{i}', nn.Dropout(0.1))
                self.net.add_module(f'out', nn.Linear(dims[-2], dims[-1]))

            def forward(self, z, c):
                x = torch.cat([z, c], dim=1)
                return self.net(x)

        class Discriminator(nn.Module):
            def __init__(self, feature_dim, cond_dim, layers):
                super().__init__()
                dims = [feature_dim + cond_dim] + layers + [1]
                self.net = nn.Sequential()
                for i in range(len(dims) - 2):
                    self.net.add_module(f'fc{i}', nn.Linear(dims[i], dims[i+1]))
                    self.net.add_module(f'lrelu{i}', nn.LeakyReLU(0.2))
                self.net.add_module(f'out', nn.Linear(dims[-2], dims[-1]))
                self.net.add_module(f'sig', nn.Sigmoid())

            def forward(self, x, c):
                inp = torch.cat([x, c], dim=1)
                return self.net(inp)

        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.generator = Generator(self.noise_dim, cond_dim, self.gen_layers, feature_dim).to(device)
        self.discriminator = Discriminator(feature_dim, cond_dim, self.disc_layers).to(device)

        gen_opt = torch.optim.Adam(self.generator.parameters(), lr=self.learning_rate, betas=(0.5, 0.999))
        disc_opt = torch.optim.Adam(self.discriminator.parameters(), lr=self.learning_rate, betas=(0.5, 0.999))
        bce = nn.BCELoss()

        real_features_t = torch.FloatTensor(features_encoded).to(device)
        real_conds_t = torch.FloatTensor(cond_scaled).to(device)
        n_samples = len(features_encoded)

        for epoch in range(self.epochs):
            indices = torch.randperm(n_samples)[:self.batch_size]
            real_f = real_features_t[indices]
            real_c = real_conds_t[indices]
            bs = real_f.shape[0]

            noise = torch.randn(bs, self.noise_dim).to(device)
            fake_f = self.generator(noise, real_c)

            disc_opt.zero_grad()
            real_out = self.discriminator(real_f, real_c)
            fake_out = self.discriminator(fake_f.detach(), real_c)
            disc_loss = 0.5 * (
                bce(real_out, torch.ones_like(real_out) * 0.9) +
                bce(fake_out, torch.zeros_like(fake_out) + 0.1)
            )
            disc_loss.backward()
            disc_opt.step()

            gen_opt.zero_grad()
            noise = torch.randn(bs, self.noise_dim).to(device)
            fake_f = self.generator(noise, real_c)
            fake_out = self.discriminator(fake_f, real_c)
            gen_loss = bce(fake_out, torch.ones_like(fake_out))
            gen_loss.backward()
            gen_opt.step()

            if (epoch + 1) % 500 == 0:
                print(f"  CGAN Epoch {epoch+1}/{self.epochs}, G_loss: {gen_loss.item():.4f}, D_loss: {disc_loss.item():.4f}")

    def fit(self, data):
        features = data[self.feature_cols].values.astype(np.float64)
        conditions = data[[self.condition_col]] if isinstance(self.condition_col, str) else data[self.condition_col]

        use_tf = self._check_tf()
        if use_tf:
            self._train_tf(features, conditions)
        else:
            self._train_torch(features, conditions)

        self._backend = 'tf' if use_tf else 'torch'
        return self

    def generate(self, n_samples, condition_values=None, condition_range=None):
        if condition_values is not None:
            cond_values = np.array(condition_values).reshape(-1, 1)
        elif condition_range is not None:
            cond_values = np.random.uniform(
                condition_range[0], condition_range[1], size=(n_samples, 1)
            )
        else:
            cond_values = self._cond_scaler.inverse_transform(
                np.random.choice(
                    self._cond_scaler.transform(
                        np.arange(1368, 1644).reshape(-1, 1)
                    ).flatten(),
                    size=n_samples
                ).reshape(-1, 1)
            )
        cond_scaled = self._cond_scaler.transform(cond_values)

        if self._backend == 'tf':
            noise = self._tf.random.normal([n_samples, self.noise_dim])
            cond_tf = self._tf.constant(cond_scaled.astype(np.float32))
            gen_input = self._tf.concat([noise, cond_tf], axis=1)
            fake_encoded = self.generator(gen_input, training=False).numpy()
        else:
            with self._torch.no_grad():
                noise = self._torch.randn(n_samples, self.noise_dim)
                cond_t = self._torch.FloatTensor(cond_scaled)
                device = next(self.generator.parameters()).device
                noise = noise.to(device)
                cond_t = cond_t.to(device)
                fake_encoded = self.generator(noise, cond_t).cpu().numpy()

        if self.use_gmm_encoding and self.gmm_encoder is not None:
            cont_indices = list(range(self._feature_dim_raw))
            fake_features = self.gmm_encoder.decode(
                fake_encoded, cont_indices,
                {idx: self.gmm_encoder.gmms[idx].n_components + 1 for idx in cont_indices}
            )
        else:
            fake_features = fake_encoded

        fake_features = self.scaler.inverse_transform(fake_features[:, :len(self.feature_cols)])
        result = pd.DataFrame(fake_features, columns=self.feature_cols)
        result[self.condition_col] = cond_values.flatten()
        return result

    def evaluate_quality(self, real_data, synth_data, real_labels=None):
        if self.tabsyndex_evaluator is None:
            self.tabsyndex_evaluator = TabSynDex()

        real_features = real_data[self.feature_cols].values.astype(np.float64)
        synth_features = synth_data[self.feature_cols].values.astype(np.float64)

        tabsyndex, scores = self.tabsyndex_evaluator.evaluate(
            real_features, synth_features, real_labels
        )
        return tabsyndex, scores


def augment_zaihuang_data(data, n_augment=500, epochs=1000):
    feature_cols = ['x', 'y', 'level']
    condition_col = 'year'

    augmentor = CGANDataAugmentor(
        feature_cols=feature_cols,
        condition_col=condition_col,
        noise_dim=32,
        gen_layers=[128, 64],
        disc_layers=[128, 64],
        epochs=epochs,
        batch_size=64,
        use_gmm_encoding=True,
        gmm_n_modes=3,
        use_tabsyndex=True,
    )
    augmentor.fit(data)
    augmented = augmentor.generate(n_augment, condition_range=(data['year'].min(), data['year'].max()))

    augmented['level'] = np.clip(np.round(augmented['level']), 1, 5)
    augmented['year'] = np.clip(np.round(augmented['year']), 1368, 1643)

    if augmentor.use_tabsyndex:
        real_features = data[feature_cols].values.astype(np.float64)
        synth_features = augmented[feature_cols].values.astype(np.float64)
        tabsyndex, scores = augmentor.evaluate_quality(data, augmented)
        print(f"  TabSynDex评估: 总分={tabsyndex:.4f}")
        for k, v in scores.items():
            print(f"    {k}: {v:.4f}")

    combined = pd.concat([data, augmented], ignore_index=True)
    print(f"数据增强完成: 原始{len(data)}条 + 合成{len(augmented)}条 = 总计{len(combined)}条")
    return combined, augmentor


def augment_jinshi_data(data, n_augment=300, epochs=1000):
    feature_cols = ['X', 'Y']
    condition_col = 'EntryYear'

    augmentor = CGANDataAugmentor(
        feature_cols=feature_cols,
        condition_col=condition_col,
        noise_dim=16,
        gen_layers=[64, 32],
        disc_layers=[64, 32],
        epochs=epochs,
        batch_size=64,
        use_gmm_encoding=True,
        gmm_n_modes=3,
        use_tabsyndex=True,
    )
    augmentor.fit(data)
    augmented = augmentor.generate(n_augment, condition_range=(data['EntryYear'].min(), data['EntryYear'].max()))

    augmented['EntryYear'] = np.clip(np.round(augmented['EntryYear']), 1368, 1643)
    augmented['EntryRank'] = '第2甲'
    augmented['level'] = 2

    if augmentor.use_tabsyndex:
        tabsyndex, scores = augmentor.evaluate_quality(data, augmented)
        print(f"  TabSynDex评估: 总分={tabsyndex:.4f}")
        for k, v in scores.items():
            print(f"    {k}: {v:.4f}")

    combined = pd.concat([data, augmented], ignore_index=True)
    print(f"进士数据增强完成: 原始{len(data)}条 + 合成{len(augmented)}条 = 总计{len(combined)}条")
    return combined, augmentor
