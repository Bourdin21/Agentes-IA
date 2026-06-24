START TRANSACTION;
ALTER TABLE `Pacientes` ADD `DigitoAfiliado` varchar(3) NULL;

ALTER TABLE `Pacientes` ADD `MutualId` int NULL;

ALTER TABLE `Pacientes` ADD `RelacionAfiliado` varchar(5) NULL;

ALTER TABLE `Pacientes` ADD `TipoDocumentoFabaId` int NULL;

CREATE TABLE `Mutuales` (
    `Id` int NOT NULL AUTO_INCREMENT,
    `IdFaba` int NOT NULL,
    `Nombre` varchar(150) NOT NULL,
    `CodigoFacturante` int NULL,
    `EsOsde` tinyint(1) NOT NULL,
    `Activo` tinyint(1) NOT NULL,
    `UltimaSincMutuales` datetime(6) NULL,
    `UltimaSincPracticas` datetime(6) NULL,
    `CreatedAt` datetime(6) NOT NULL,
    `CreatedByUserId` longtext NULL,
    `UpdatedAt` datetime(6) NULL,
    `UpdatedByUserId` longtext NULL,
    `DeletedAt` datetime(6) NULL,
    `DeletedByUserId` longtext NULL,
    PRIMARY KEY (`Id`)
);

CREATE TABLE `UnidadesBioquimicasFabaCodigos` (
    `Id` int NOT NULL AUTO_INCREMENT,
    `MutualId` int NOT NULL,
    `CodigoFaba` int NOT NULL,
    `NombreFaba` varchar(200) NOT NULL,
    `Activo` tinyint(1) NOT NULL,
    `UnidadBioquimicaId` int NULL,
    PRIMARY KEY (`Id`),
    CONSTRAINT `FK_UnidadesBioquimicasFabaCodigos_Mutuales_MutualId` FOREIGN KEY (`MutualId`) REFERENCES `Mutuales` (`Id`) ON DELETE CASCADE,
    CONSTRAINT `FK_UnidadesBioquimicasFabaCodigos_UnidadesBioquimicas_UnidadBio~` FOREIGN KEY (`UnidadBioquimicaId`) REFERENCES `UnidadesBioquimicas` (`Id`) ON DELETE SET NULL
);

CREATE INDEX `IX_Pacientes_MutualId` ON `Pacientes` (`MutualId`);

CREATE UNIQUE INDEX `IX_Mutuales_IdFaba` ON `Mutuales` (`IdFaba`);

CREATE UNIQUE INDEX `IX_UnidadesBioquimicasFabaCodigos_MutualId_CodigoFaba` ON `UnidadesBioquimicasFabaCodigos` (`MutualId`, `CodigoFaba`);

CREATE INDEX `IX_UnidadesBioquimicasFabaCodigos_UnidadBioquimicaId` ON `UnidadesBioquimicasFabaCodigos` (`UnidadBioquimicaId`);

ALTER TABLE `Pacientes` ADD CONSTRAINT `FK_Pacientes_Mutuales_MutualId` FOREIGN KEY (`MutualId`) REFERENCES `Mutuales` (`Id`) ON DELETE SET NULL;

INSERT INTO `__EFMigrationsHistory` (`MigrationId`, `ProductVersion`)
VALUES ('20260618022201_AddFabaMutualYAnalitos', '10.0.2');

COMMIT;

