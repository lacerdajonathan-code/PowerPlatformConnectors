# Script PowerShell para importar fluxo do Power Automate
# Requer módulos: Microsoft.PowerApps.Administration.PowerShell e Microsoft.PowerApps.PowerShell

param(
    [Parameter(Mandatory=$true)]
    [string]$EnvironmentName,
    
    [Parameter(Mandatory=$false)]
    [string]$FlowDisplayName = "Excel para Planner - Criação de Tarefas",
    
    [Parameter(Mandatory=$false)]
    [string]$JsonFilePath = "./power-automate-excel-to-planner.json"
)

# Função para instalar módulos necessários
function Install-RequiredModules {
    $modules = @(
        "Microsoft.PowerApps.Administration.PowerShell",
        "Microsoft.PowerApps.PowerShell"
    )
    
    foreach ($module in $modules) {
        if (!(Get-Module -ListAvailable -Name $module)) {
            Write-Host "Instalando módulo $module..." -ForegroundColor Yellow
            Install-Module -Name $module -Force -AllowClobber -Scope CurrentUser
        }
    }
}

# Função principal
function Import-FlowToEnvironment {
    param(
        [string]$EnvironmentName,
        [string]$FlowDisplayName,
        [string]$JsonFilePath
    )
    
    try {
        # Verificar se o arquivo JSON existe
        if (!(Test-Path $JsonFilePath)) {
            throw "Arquivo JSON não encontrado: $JsonFilePath"
        }
        
        # Ler o conteúdo do arquivo JSON
        $flowDefinition = Get-Content $JsonFilePath -Raw | ConvertFrom-Json
        
        # Conectar ao Power Platform
        Write-Host "Conectando ao Power Platform..." -ForegroundColor Green
        Add-PowerAppsAccount
        
        # Obter o ambiente
        $environment = Get-AdminPowerAppEnvironment | Where-Object { $_.DisplayName -eq $EnvironmentName -or $_.EnvironmentName -eq $EnvironmentName }
        
        if (!$environment) {
            throw "Ambiente '$EnvironmentName' não encontrado"
        }
        
        Write-Host "Ambiente encontrado: $($environment.DisplayName)" -ForegroundColor Green
        
        # Criar o fluxo
        $flowProperties = @{
            "displayName" = $FlowDisplayName
            "definition" = $flowDefinition
            "state" = "Stopped"  # Criar como parado para configuração
        }
        
        # Converter para JSON
        $flowJson = $flowProperties | ConvertTo-Json -Depth 100
        
        # Criar o fluxo usando a API REST
        $apiVersion = "2016-11-01"
        $flowsUrl = "https://api.flow.microsoft.com/providers/Microsoft.ProcessSimple/environments/$($environment.EnvironmentName)/flows?api-version=$apiVersion"
        
        $headers = @{
            "Authorization" = "Bearer $(Get-PowerAppsAuthToken)"
            "Content-Type" = "application/json"
        }
        
        Write-Host "Criando fluxo '$FlowDisplayName'..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri $flowsUrl -Method Post -Headers $headers -Body $flowJson
        
        if ($response) {
            Write-Host "✓ Fluxo criado com sucesso!" -ForegroundColor Green
            Write-Host "ID do Fluxo: $($response.name)" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "PRÓXIMOS PASSOS:" -ForegroundColor Yellow
            Write-Host "1. Acesse o Power Automate: https://flow.microsoft.com" -ForegroundColor White
            Write-Host "2. Navegue até 'Meus fluxos'" -ForegroundColor White
            Write-Host "3. Localize o fluxo '$FlowDisplayName'" -ForegroundColor White
            Write-Host "4. Configure as conexões necessárias:" -ForegroundColor White
            Write-Host "   - Excel Online (OneDrive)" -ForegroundColor White
            Write-Host "   - Microsoft Planner" -ForegroundColor White
            Write-Host "   - Outlook (opcional)" -ForegroundColor White
            Write-Host "5. Atualize os parâmetros no fluxo:" -ForegroundColor White
            Write-Host "   - DRIVE_ID: ID do OneDrive" -ForegroundColor White
            Write-Host "   - FILE_ID: ID do arquivo Excel" -ForegroundColor White
            Write-Host "   - PLAN_ID: ID do plano no Planner" -ForegroundColor White
            Write-Host "   - BUCKET_ID: ID do bucket no Planner" -ForegroundColor White
            Write-Host "   - USER_ID: ID do usuário para atribuição" -ForegroundColor White
            Write-Host "6. Ative o fluxo" -ForegroundColor White
            
            return $response
        }
    }
    catch {
        Write-Host "Erro ao importar fluxo: $_" -ForegroundColor Red
        throw
    }
}

# Função auxiliar para obter token de autenticação
function Get-PowerAppsAuthToken {
    $token = Get-PowerAppsAuthTokenFromCache
    if (!$token) {
        Add-PowerAppsAccount
        $token = Get-PowerAppsAuthTokenFromCache
    }
    return $token
}

function Get-PowerAppsAuthTokenFromCache {
    $context = [Microsoft.IdentityModel.Clients.ActiveDirectory.AuthenticationContext]::new("https://login.microsoftonline.com/common")
    $result = $context.AcquireTokenSilentAsync("https://api.flow.microsoft.com", $clientId).Result
    return $result.AccessToken
}

# Executar o script
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  IMPORTADOR DE FLUXO POWER AUTOMATE  " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Instalar módulos necessários
Install-RequiredModules

# Importar o fluxo
Import-FlowToEnvironment -EnvironmentName $EnvironmentName -FlowDisplayName $FlowDisplayName -JsonFilePath $JsonFilePath